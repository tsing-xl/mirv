# Returns a file's sha256.

from pathlib import Path
from hashlib import sha256


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