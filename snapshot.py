# Take a snapshot for ordered path.

from pathlib import Path
from shutil import copy2
from os import replace
from datetime import datetime
from json import dumps, loads
from json import JSONDecodeError

from walk import walk_through
from hash import sha256_of
from log import logout
from checkup import mirv_checkup, strict_mirv_checkup, venv_checkup

def write_snapshot(workspace_path: Path, files: dict[str, str]) -> None: 
    '''Write the shapshot json file in .mirv/snapshot.'''

    # Validate checkup: if .mirv exists.
    _mirv: Path = workspace_path / '.mirv'
    mirv_checkup(workspace_path)

    # Timesnap for now
    created = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

    # Create a temp file so that incompleted json snapshot
    # will not loaded by glob('*.json').
    temp_file: Path = _mirv / 'snapshot' / 'writing.tmp'
    temp_file.write_text(dumps(
        {
            'created': created, 
            'files': files, 
        }, 
        indent = 2, 
    ), encoding = 'utf-8')

    # Replace the name of temp file.
    final: Path = _mirv / 'snapshot' / f'{created}.json'
    replace(temp_file, final)

def take_snapshot(workspace_path: Path) -> None: 
    '''Create a snapshot for workspace's .venv folder.'''

    files: dict[str, str] = {}

    # Validate checkup: if .venv exists.
    _venv: Path = workspace_path / '.venv'
    venv_checkup(workspace_path)

    # Validate checkup: if .mirv exists.
    _mirv: Path = workspace_path / '.mirv'
    _storage: Path = _mirv / 'storage'

    strict_mirv_checkup(workspace_path)

    # Walk through .venv first.
    for relative_path in walk_through(_venv): 

        # Calculate the hash of file first.
        digest = sha256_of(_venv / relative_path)

        # Store the file and skips the same file.
        target: Path = _storage / digest

        # Copy the file (contains file metadata)
        if not target.is_file():
            copy2(
                _venv / relative_path, 
                target, 
            )

        files[relative_path] = digest

    # Function: write_snapshot_json
    write_snapshot(workspace_path, files)

def restore_snapshot(workspace_path: Path, ordered_state: Path) -> None: 
    '''Put every file of the state back into venv.'''

    # Checkup: .mirv exists.
    _mirv: Path = workspace_path / '.mirv'
    strict_mirv_checkup(workspace_path)

    # Be sure that the .venv exists.
    _venv: Path = workspace_path / '.venv'
    _venv.mkdir(parents = True, exist_ok = True)

    # Check if manifest can load through loads.
    # Dnmd 累了 先做个简单的验证 之后的事情之后弄了
    try: 

        manifest: dict = loads(ordered_state.read_text('utf-8'))
        if not isinstance(manifest, dict): 

            # Print a debug log and quit.
            logout('Your state is broken. Please try another state.')
            raise SystemExit

    except JSONDecodeError: 
        # Print a debug log and quit.
        logout('Your state is broken. Please try another state.')
        raise SystemExit

    # Probably dict
    known_files: dict = manifest['files']

    # Put back every file to the ordered state.
    for relative, digest in known_files.items(): 

        # Translate the relative path to absolute path.
        target: Path = _venv / relative
        
        # Before copying, create the directory first.
        target.parent.mkdir(parents = True, exist_ok = True)

        # Copy.
        copy2(_mirv / 'storage' / digest, target)

        # 哎呀可滚蛋吧多余文件关我屁事
        # 我又不是你跌天天跟在你屁股后面给你收拾烂摊子
        # 不做 滚