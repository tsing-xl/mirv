from pathlib import Path
from hashlib import sha256
from shutil import copy2
from datetime import datetime
from json import dumps, loads
from os import replace

def walk_through_venv(venv: Path) -> list[tuple[str, int, float]]: 
    '''Walk through .venv files.'''

    entries: list = []

    # Walk through
    for path in venv.rglob('*'): 

        # Not a file, a .pyc file, in __pycache__: skip.
        if not path.is_file(): continue
        if path.suffix == '.pyc' or '__pycache__' in path.parts: continue

        # Record each file's status, for lightweighted-diff.
        status = path.stat()

        # Add result into list.
        # Here we record relative path instead of resolved path.
        # 
        # Also, add a as_posix() for solve backward-slash problems on NT.
        entries.append((
            path.relative_to(venv).as_posix(), 
            status.st_size, # File size
            status.st_mtime, # Last written/update time
        ))

    # Return sorted (from A-Z) list.
    return sorted(entries)

def sha256_of(path: Path) -> str: 
    '''Return the sha256 string of ordered file.'''

    # Initialize the sha256 object for chunk-reading.
    digest = sha256()

    # Read files in binary mode for all files.
    with path.open('rb') as file: 

        # Here 1 << 20 means read 1Mib per chunk.
        for chunk in iter(lambda: file.read(1 << 20), b''): 
            digest.update(chunk)

    # Return string result.
    return digest.hexdigest()

def store(store: Path, source: Path, digest: str): 
    '''Copy content into the store. Automatically skips duplicates.'''

    target_file: Path = store / digest

    # If target_file is already exists, skip.
    if not target_file.exists(): copy2(source, target_file)

def write_snapshot_json(path: Path, files: dict[str, str]) -> Path: 
    '''Write the snapshot file to given path.'''

    # The timestamp of now.
    created = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

    # Create a temp file so that incompleted json snapshot
    # will not loaded by glob('*.json').
    temp_file: Path = path / 'snapshot' / 'writing.tmp'
    temp_file.write_text(dumps(
        {
            'created': created, 
            'files': files, 
        }, 
        indent = 2, 
    ), encoding = 'utf-8')

    # The final file name of the snapshot.
    final: Path = path / 'snapshot' / f'{created}.json'
    replace(temp_file, final)

    # Return the final snapshot's path object.
    return final

def snapshot(mirv: Path, path: Path) -> Path: 
    '''Create a snapshot for current venv.'''

    files: dict[str, str] = {}
    
    # walk_through_venv returns (path, size, time) here.
    for relative, _, _ in walk_through_venv(path): 

        # Calculate the hash of file.
        digest = sha256_of(path / relative)

        # Store the file with hashes file name.
        store(mirv / 'store', path / relative, digest)

        # Let the snapshot.json records.
        files[relative] = digest

    # Return the status of write_snapshot_json for later process.
    return write_snapshot_json(mirv, files)

def initialize_mirv_path(workspace: Path) -> None: 
    '''
    Initializes the path of mirv.
    
    The workspace parameter receives a getcwd() result in default.
    '''

    # Create the snapshot directory.
    (workspace / '.mirv' / 'store').mkdir(parents = True, exist_ok = True)
    (workspace / '.mirv' / 'snapshot').mkdir(parents = True, exist_ok = True)

def restore(mirv: Path, venv: Path, state: Path) -> None: 
    '''Put every file of the state back into venv.'''

    manifest: dict = loads(state.read_text('utf-8'))
    known_files = manifest['files']

    # Put back every file to the ordered state.
    for relative, digest in known_files.items(): 

        # Translate the relative path to absolute path.
        target: Path = venv / relative

        # Before copying, create the directory first.
        target.parent.mkdir(parents = True, exist_ok = True)

        # Copy.
        copy2(mirv / 'store' / digest, target)

    # Report the extra file in current venv.
    for relative, _, _ in walk_through_venv(venv): 
        if relative not in known_files: print(f'mirv: extra file found: {relative}')

