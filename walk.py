# Walk through the environment and return a list.

from pathlib import Path


def walk_through(start_path: Path) -> list[str]: 
    '''Walk through from ordered path.'''

    entries: list = []
    
    # Walk through
    for path in start_path.rglob('*'): 
    
        # Not a file, a .pyc file, in __pycache__: skip.
        if not path.is_file(): continue
        if path.suffix == '.pyc' or '__pycache__' in path.parts: continue
    
        # Add result into list.
        # Here we record relative path instead of resolved path.
        # 
        # Also, add a as_posix() for solve backward-slash problems on NT.
        entries.append(
            path.relative_to(start_path).as_posix(), 
        )
    
    # Return sorted (from A-Z) list.
    return sorted(entries)