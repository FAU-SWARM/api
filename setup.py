import os
import sys
from setuptools import find_packages, setup
if sys.version_info[0] > 2:
    import configparser
else:
    import ConfigParser as configparser


THIS_DIR = os.path.dirname(__file__)
REQUIREMENTS = os.path.join(THIS_DIR, 'requirements.txt')
README = os.path.join(THIS_DIR, 'README.md')
ABOUT = os.path.join(THIS_DIR, 'ABOUT')
config = configparser.ConfigParser()
config.read(ABOUT)
if sys.version_info[0] == 2:
    name = config.get('about', 'name', 'apilib')
    version = config.get('about', 'version', '0.0.0')
else:
    name = config['about'].get('name', 'apilib')
    version = config['about'].get('version', '0.0.0')

requirements = []
with open(REQUIREMENTS, 'rb') as r:
    requirements += [line.decode('UTF-8') for line in r.readlines()]
long_description = ''
with open(README, 'rb') as r:
    long_description = r.read().decode('UTF-8')


setup(
    name=name,
    version=version,
    description='API Library',
    long_description=long_description,
    author='',
    author_email='ccarl2@fau.edu',
    url='https://github.com/FAU-SWARM/api',
    packages=find_packages(
        exclude=['dist', 'build', 'docs', 'test']
    ),
    install_requires=requirements,
)
