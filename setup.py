import os
import sys
from subprocess import check_output, SubprocessError

DOCLINES = (__doc__ or '').split("\n")

if sys.version_info[:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 required.")


MAJOR = 0
MINOR = 2
MICRO = 2
IS_RELEASED = False
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


def git_version():
    try:
        rev = check_output(['git', 'rev-parse', 'HEAD'])
        return rev.strip().decode('ascii')
    except (SubprocessError, OSError):
        return "Unknown"


def get_version_info():
    full_version = VERSION
    if os.path.exists('.git'):
        git_revision = git_version()
    else:
        git_revision = "Unknown"

    if not IS_RELEASED:
        full_version += '.dev0+' + git_revision[:7]

    return full_version, git_revision


def write_version_py(filename='NetworkUtilities/version.py'):
    full_version, git_revision = get_version_info()

    content = "# Version file generated by setup.py \n\n" \
              f"short_version = '{VERSION}' \n" \
              f"version = '{VERSION}' \n" \
              f"full_version = '{full_version}' \n" \
              f"git_revision = '{git_revision}' \n" \
              f"release = {str(IS_RELEASED)} \n" \
              "\n\n" \
              f"if not release: \n" \
              f"    version = full_version \n"

    with open(filename, 'w') as f:
        f.write(content)


def setup_package():
    from setuptools import setup
    write_version_py()

    setup(
        name='NetworkUtilities',
        version=get_version_info()[0],
        description='A quick project allowing to calculate subnetwork ranges easily',
        url='https://github.com/BioTheWolff/NetworkUtilities',
        project_urls={
            'Source Code': 'https://github.com/BioTheWolff/NetworkUtilities',
            'Bug Tracker': 'https://github.com/BioTheWolff/NetworkUtilities/issues',
        },

        author='Fabien Z.',
        author_email='contact.biowolf@gmx.fr',
        maintainer='Fabien Z.',
        maintainer_email='contact.biowolf@gmx.fr',

        license='MIT',
        packages=[
            'NetworkUtilities',
            'NetworkUtilities.core',
            'NetworkUtilities.utils'
        ],
        install_requires=[
            "pytest",
        ],

        python_requires='>=3.6',
        zip_safe=False,
        scripts=['bin/runtests']
    )


if __name__ == '__main__':
    setup_package()
