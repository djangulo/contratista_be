from subprocess import call
from argparse import ArgumentParser

parser = ArgumentParser(description='Install DRF-seed project')
parser.add_argument(
    'project_name',
    help="""Name for the DRF project. Positional and must be first. Required.""",
    action='store',
)
parser.add_argument(
    '--api-url-prefix',
    help="""Prefix for the API endpoints.""",
    action='store',
)
parser.add_argument(
    '--proxy',
    help="""Proxy information for pip to consume.""",
    action='store',
)
parser.add_argument(
    '--auth-type',
    help="""Default authentication class(es) for DEFAULT_AUTHENTICATION_CLASSES in settings.py. 
Options: any combination of 'basic', 'token', 'session'. Will be added in the order provided"""

)
