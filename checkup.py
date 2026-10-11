# Checkup if .mirv or .venv is missing.

from pathlib import Path

from log import logout

# Structure of .mirv: 
# .mirv
#   | snapshot
#   | storage
# 
# The json snapshot file saved in `snapshot` folder.
# File blobs with hashed name saved in `storage` folder.

def mirv_checkup(workspace_path: Path) -> None: 
    '''
    Checkup if .mirv folder is missing.

    Strict raise a SystemExit if checkup failed.
    '''

    _mirv: Path = workspace_path / '.mirv'

    # If checkup failed, raise a SystemExit instead of 
    # returning a code as a result.
    if not _mirv.is_dir(): 

        # Print a debug log and exit.
        logout('Missing .mirv folder in current workspace. Have you initialized mirv here?')
        raise SystemExit

def strict_mirv_checkup(workspace_path: Path) -> None: 
    '''
    Check up if .mirv, snapshot and storage is missing.
    
    Strict raise a SystemExit if checkup failed.
    '''

    # Before strict checkup, make a simply checkup first.
    mirv_checkup(workspace_path)

    _mirv: Path = workspace_path / '.mirv'
    _snapshot: Path = _mirv / 'snapshot'
    _storage: Path = _mirv / 'storage'

    if not _snapshot.is_dir() or not _storage.is_dir(): 

        # Print a debug log and exit.
        logout('.mirv structure incomplete. Try initialize again.')
        raise SystemExit

# TODO: Support any kind of virtual environment.
def venv_checkup(workspace_path: Path) -> None: 
    '''
    Checkup if .venv is missing.
    
    Strict raise a SystemExit if checkup failed.
    '''

    _venv: Path = workspace_path / '.venv'

    if not _venv.is_dir(): 

        # Print a debug log and exit.
        logout('Mirv have nothing to record: .venv is empty or missing.')
        raise SystemExit