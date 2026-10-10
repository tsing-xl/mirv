# Log module for mirv.

def logout(*strings: str, end: str = '\n') -> None: 
    '''Print out texts on console/terminal.'''

    print('mirv:', ''.join(strings), end = end)