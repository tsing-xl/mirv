# 
# Mirage Virtual Environment Snapshot Manager: Mirv
# Copyright (c) tsing-xl under PNL 1.0.0.
# 
# See https://polyformproject.org/licenses/noncommercial/1.0.0
# 

from pathlib import Path
from argparse import ArgumentParser

from snapshot import take_snapshot, restore_snapshot
from log import logout


# Mirv constants.
__version__: str = '0.1'

# Agrparse argument parser builder.
def parser_builder() -> ArgumentParser: 
    '''
    Build a parser for mirv.
    '''

    # Build a ArgumentParser first.
    # TODO: Better description.
    parser = ArgumentParser(
        prog = 'mirv', 
        description = 'Take a snapshot for your virtual environment, '
        'and restore it to ordered state.'
    )

    # Sub parser. -> mirv <operation>.
    operation_parser = parser.add_subparsers(dest = 'operation', required = True)

    # Operation: init
    operation_init = operation_parser.add_parser(
        'init', 
        help = 'Initialize the mirv storage library.'
    )
    operation_init.add_argument('--workspace', type = Path, default = Path.cwd())

    # Operation: snapshot
    operation_snapshot = operation_parser.add_parser(
        'snapshot', 
        help = 'Take a json snapshot for current environment\'s state.'
    )
    operation_snapshot.add_argument('--workspace', type = Path, default = Path.cwd())

    # Operation: restore
    operation_restore = operation_parser.add_parser(
        'restore', 
        help = 'Restore the environment to an ordered state.'
    )
    operation_restore.add_argument('state', type = Path, help = 'The snapshot json file to restore.')
    operation_restore.add_argument('--workspace', type = Path, default = Path.cwd())

    # Return the completed parser.
    return parser

# Main guard.
if __name__ == '__main__': 

    # Receive arguments from console/tty.
    arguments = parser_builder().parse_args()

    if arguments.operation == 'init': 

        # Initialize the folder.
        # Here add a Path wrap for passing type checking.
        _mirv = Path(arguments.workspace) / '.mirv'

        _snapshot = _mirv / 'snapshot'
        _storage = _mirv / 'storage'

        # Create it.
        _snapshot.mkdir(parents = True, exist_ok = True)
        _storage.mkdir(parents = True, exist_ok = True)

        logout('Done.')

    elif arguments.operation == 'snapshot': 
        take_snapshot(arguments.workspace)

    elif arguments.operation == 'restore': 
        restore_snapshot(arguments.workspace, arguments.state)