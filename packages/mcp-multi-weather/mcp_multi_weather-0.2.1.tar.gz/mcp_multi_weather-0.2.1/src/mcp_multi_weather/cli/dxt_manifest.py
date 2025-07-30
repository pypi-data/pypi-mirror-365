import sys
import tomllib
from string import Template
from typing import Any


def read_package_config() -> dict[str, Any]:
    with open('./pyproject.toml', 'rb') as f:
        config = tomllib.load(f)

    return config


def read_manifest_template() -> Template:
    with open('./manifest.template.json', 'r') as file:
        content = file.read()

    return Template(content)


def write_manifest_file(content: str) -> None:
    with open('./manifest.json', 'w') as file:
        file.write(content)


def main() -> None:
    package_config = read_package_config()
    manifest_template = read_manifest_template()

    result = manifest_template.substitute(
        APP_NAME=package_config['project']['name'],
        APP_VERSION=package_config['project']['version'],
        APP_DESCRIPTION=package_config['project']['description'],
        APP_LONG_DESCRIPTION=package_config['project']['description'],
        APP_LICENSE=package_config['project']['license'],
        APP_PYTHON_VERSION=package_config['project']['requires-python'],
        AUTHOR_NAME=package_config['project']['authors'][0]['name'],
        AUTHOR_EMAIL=package_config['project']['authors'][0].get('email', ''),
        AUTHOR_URL=package_config['project'].get('urls', {}).get('Homepage', ''),
        SITE_PACKAGES_PATH=f'.venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages',
    )

    write_manifest_file(result)


if __name__ == '__main__':
    main()
