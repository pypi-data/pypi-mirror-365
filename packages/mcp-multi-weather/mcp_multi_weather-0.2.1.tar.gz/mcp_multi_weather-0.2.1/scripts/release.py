#!/usr/bin/env python3

import os
import subprocess
import sys
import tomllib
from pathlib import Path

SCRIPT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


#
# Helpers
#


def get_project_version() -> str:
    """
    Loads the version from the pyproject.toml file
    """
    with open(SCRIPT_PATH.parent / 'pyproject.toml', 'rb') as f:
        pyproject = tomllib.load(f)

    return pyproject['project']['version']


def get_tag(tag_name: str) -> bool:
    """
    Checks if the current git tag matches the project version.
    """
    subprocess.check_output(['git', 'fetch', '--tags'])
    tag = subprocess.check_output(['git', 'tag', '-l', f'{tag_name}'])

    return tag_name == tag.strip().decode('utf-8')


#
# Commands
#


def check_release() -> int:
    project_version = f'v{get_project_version()}'
    print(f'Project Version: {project_version}')

    if not get_tag(project_version):
        print(f'Tag for version {project_version} not found')
        return 1

    print(f'Tag for version {project_version} exists')
    return 0


#
# Entry Point
#

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} (get-version|check-release)')
        sys.exit(-1)

    match sys.argv[1]:
        case 'get-version':
            print(f'v{get_project_version()}')
            sys.exit(0)
        case 'check-release':
            output = check_release()
            sys.exit(output)
        case _:
            print(f'Unknown command: {sys.argv[1]}')
            sys.exit(1)
