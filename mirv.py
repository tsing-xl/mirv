from pathlib import Path
from shutil import copy2
from datetime import datetime
from json import dumps, loads
from os import replace

from walk import walk_through
from hash import sha256_of
from log import logout

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
    
    # walk_through_venv returns path here.
    for relative in walk_through(path): 

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
    for relative in walk_through(venv): 
        if relative not in known_files: logout(f' extra file found: {relative}')


# Main entrance of tool.
if __name__ == '__main__': 

    from sys import argv

    # e.g.: python -m mirv
    if len(argv) <= 1: 
        logout('usage: mirv <operation> <optional-parameter>')
        raise SystemExit
    
    # Here the length of argv must be >= 2.
    operation = argv[1]

    # Operation initialize.
    if operation == 'init': 
        initialize_mirv_path(Path.cwd())
        logout('done.')