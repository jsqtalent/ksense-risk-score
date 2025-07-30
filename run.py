import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli import cli

if __name__ == '__main__':
    cli()
