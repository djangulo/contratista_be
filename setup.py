import argparse
import os
import re
import sys
from importlib import import_module
from subprocess import Popen, PIPE, run

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SetupDrfSeed:

    def __init__(self):
        self._sanity_checks()
        self._parse_arguments()

    def _sanity_checks(self):
        try:
            outs, errs = Popen('sed --version', stdout=PIPE).communicate(timeout=5)
        except FileNotFoundError:
            sys.exit('ERROR: sed is not installed or is not found in $PATH')
        try:
            outs, errs = Popen('git --version', stdout=PIPE).communicate(timeout=5)
        except FileNotFoundError:
            sys.exit('ERROR: git is not installed or is not found in $PATH')
        try:
            outs, errs = Popen('python3.6 --version', stdout=PIPE).communicate(timeout=5)
            self.python_caller = 'python3.6'
        except FileNotFoundError:
            try:
                outs, errs = Popen('python3 --version', stdout=PIPE).communicate(timeout=5)
                if '3.6' in str(outs):
                    self.python_caller = 'python3'
                else:
                    sys.exit('This script only compatible with python >= 3.6.1')
            except FileNotFoundError:
                try:
                    outs, errs = Popen('python --version', stdout=PIPE).communicate(timeout=5)
                    if '3.6' in str(outs):
                        self.python_caller = 'python'
                    else:
                        sys.exit('This script only compatible with python >= 3.6.1')
                except FileNotFoundError:
                    sys.exit('ERROR: python is not installed or is not found in $PATH')

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(description="Setup basic drf_seed project")
        parser.add_argument('project_name', action='store', type=str, nargs='?',
            help='Name for the DRF project')
        parser.add_argument('--api-url-prefix', action='store', type=str, nargs='?',
            const='api/v1/',
            help='Prefix for the API endpoints')
        parser.add_argument('--proxy', action='store',type=str,
            help='Instructs pip to use these proxy credentials')
        parser.add_argument('--auth', action='store', type=str, nargs='+',
            choices=['basic', 'token', 'session'],
            default=['token'],
            help='Sets DEFAULT_AUTHENTICATIN_CLASSES in settings.py')
        parser.add_argument('--router', action='store', type=str, nargs=1,
            choices=['simple', 'default', 'none'],
            default='default',
            help='Router to use, if any')
        parser.add_argument('--pagination', action='store', type=str, nargs='?',
            choices=['page', 'limitoffset', 'cursor', 'none'],
            const='page',
            help='Sets DEFAULT_PAGINATION_CLASS in settings.py')
        parser.add_argument('--page-size', action='store', type=int, nargs='?',
            const=20,
            default=20,
            help='Integer to set page size, ignored if --pagination is not set. If '
            '--pagination is provided, will default to 20 if not set.')
        parser.add_argument('--throttling', action='store', type=str, nargs='+',
            help='Sets DEFAULT_THROTTLE_CLASSES in settings.py')
        parser.add_argument('--static', action='store', type=str, nargs='?',
            const='static')
        parser.add_argument('--media-root', action='store', type=str, nargs='?',
            const='media')
        parser.add_argument('--media-url', action='store', type=str, nargs='?',
            const='media')
        self._args = parser.parse_args()

    def _create_virtualenv(self):
        if 'virtualenv' not in os.listdir(BASE_DIR):
            if 'win' in sys.platform:
                command = f'{self.python_caller} -m venv {BASE_DIR}\\virtualenv'
                run(command, stdout=PIPE)
            else:
                command = f'{self.python_caller} -m venv {BASE_DIR}/virtualenv'
                run(command, stdout=PIPE)

    def _install_dependencies(self, proxy=None):
        if 'win' in sys.platform:
            command = f'{BASE_DIR}\\virtualenv\\Scripts\\pip '
            command += f"--proxy {proxy  + ' ' if proxy else ''}"
            command += f'install -r {BASE_DIR}\\requirements.txt'
            run(command)
        else:
            command = f'{BASE_DIR}/virtualenv/bin/pip '
            command += f"--proxy {proxy + ' ' if proxy else ''}"
            command += f'install -r {BASE_DIR}/requirements.txt'
            run(command)

    def _rename_drf_seed_instances(self, project_name):
        run(f'cd {BASE_DIR}')
        if 'drf_seed' in os.listdir(BASE_DIR):
            if 'win' in sys.platform:
                run(f'sed -i s:drf_seed:{project_name}:g drf_seed/*')
                run(f'move drf_seed {project_name}')
            else:
                run(f'sed -i s:drf_seed:{project_name}:g drf_seed/* && mv drf_seed')
                run(f'mv drf_seed {project_name}')


    def _set_router(self, project_name, router=None):
        _ROUTERS = {
            'simple': 'SimpleRouter',
            'default': 'DefaultRouter',
            'none': None,
        }
        if router:
            if router == 'none':
                run(f'''sed -i "/router/d" {project_name}/urls.py''')
            else:
                run(f'''sed -i "s:DefaultRouter:{_ROUTERS[router]}:g {project_name}/urls.py''')

    def _set_auth_classes(self, project_name, auth_classes=None):
        _AUTH = {
            'key': 'DEFAULT_AUTHENTICATION_CLASSES',
            'token': 'rest_framework.authentication.TokenAuthentication',
            'session': 'rest_framework.authentication.SessionAuthentication',
            'basic': 'rest_framework.authentication.BasicAuthentication',
        }
        if auth_classes:
            try:
                REST_FRAMEWORK = __import__(
                    f'{project_name}.settings',
                    globals(),
                    locals(),
                     ['REST_FRAMEWORK']
                ).REST_FRAMEWORK
                if _AUTH['key'] in REST_FRAMEWORK.keys():
                    print(f"{_AUTH['key']} exists, and contains: ")
                    for v in REST_FRAMEWORK[_AUTH['key']]:
                        print('\t' + v)
                    print('\tSkipping, override manually')
                else:
                    raise KeyError(f"{_AUTH['key']} not found, creating...")
            except ModuleNotFoundError:
                sys.exit(f'Could not locate {project_name}/settings.py, was '
                        'this script run from the root dir?')
            except KeyError:
                run(f"sed -i '/REST_FRAMEWORK/a\    ),' {project_name}/settings.py")
                for a in auth_classes:
                    run(f"""sed -i "/REST_FRAMEWORK/a\        '{_AUTH[a]}'," {project_name}/settings.py""")
                run(f"""sed -i "/REST_FRAMEWORK/a\    '{_AUTH['key']}': (" {project_name}/settings.py""")

    def _set_pagination(self, project_name, pag=None, size=20):
        PAG = {
            'key': 'DEFAULT_PAGINATION_CLASS',
            'size_key': 'PAGE_SIZE',
            'page': 'rest_framework.pagination.PageNumberPagination',
            'limitoffset': 'rest_framework.pagination.LimitOffsetPagination',
            'cursor': 'rest_framework.pagination.CursorPagination',
        }
        if pag:
            if pag == 'none':
                run(f'''sed -i "/{PAG['key']}/d" {project_name}/settings.py''')
                run(f'''sed -i "/{PAG['size_key']}/d" {project_name}/settings.py''')
            else:
                try:
                    REST_FRAMEWORK = __import__(
                        f'{project_name}.settings',
                        globals(),
                        locals(),
                        ['REST_FRAMEWORK']
                    ).REST_FRAMEWORK
                    if PAG['key'] in REST_FRAMEWORK.keys():
                        pag_val = REST_FRAMEWORK[PAG['key']]
                        size_val = REST_FRAMEWORK[PAG['size_key']]
                        print(f"{PAG['key']} exists, its value is: {pag_val}, with size {size_val} ")
                        print(f'Replacing {pag_val} with {PAG[pag]}')
                        print(f"Replacing {PAG['size_key']}: {size_val} with {PAG['size_key']}: {size}")
                        run(f'''sed -i "s/{pag_val}/{PAG[pag]}/g" {project_name}/settings.py''')
                        run(f'''sed -i "s/'{PAG['size_key']}': {size_val},/'{PAG['size_key']}': {size},/g" {project_name}/settings.py''')
                    else:
                        raise KeyError(f"{PAG['key']} not found, creating...")
                except ModuleNotFoundError:
                    sys.exit(f'Could not locate {project_name}/settings.py, was '
                            'this script run from the root dir?')
                except KeyError:
                    run(f"""sed -i "/REST_FRAMEWORK/a\    '{PAG['key']}': '{PAG[pag]}'," {project_name}/settings.py""")
                    run(f'''sed -i "/{PAG['key']}/a\    '{PAG['size_key']}': {size}," {project_name}/settings.py''')
    
    def _set_throttling(self, project_name, throttle_classes=None):
        _THROTTLE = {
            'classes': 'DEFAULT_THROTTLE_CLASSES',
            'rates': 'DEFAULT_THROTTLE_RATES',
            'anon': 'rest_framework.throttling.AnonRateThrottle',
            'user': 'rest_framework.throttling.UserRateThrottle',
        }
        # build scopes dict = {'anon': '1000/day', 'user': '1000/day', ...}
        scopes = {s.split('=')[0]: s.split('=')[1] for s in throttle_classes}
        # set default classes:
        if throttle_classes:
            try:
                REST_FRAMEWORK = __import__(
                    f'{project_name}.settings',
                    globals(),
                    locals(),
                     ['REST_FRAMEWORK']
                ).REST_FRAMEWORK
                if _THROTTLE['rates'] in REST_FRAMEWORK.keys():
                    print(f"{_THROTTLE['rates']} exists, and contains: ")
                    for k, v in REST_FRAMEWORK[_THROTTLE['rates']].items():
                        print('\t' + k + ': ' + v)
                    
                else:
                    raise KeyError(f"{_THROTTLE['key']} not found, creating...")
            except ModuleNotFoundError:
                sys.exit(f'Could not locate {project_name}/settings.py, was '
                        'this script run from the root dir?')
            except KeyError:
                pass
                # run(f"sed -i '/REST_FRAMEWORK/a\    ),' {project_name}/settings.py")
                # for a in auth_classes:
                #     run(f"""sed -i "/REST_FRAMEWORK/a\        '{_AUTH[a]}'," {project_name}/settings.py""")
                # run(f"""sed -i "/REST_FRAMEWORK/a\    '{_AUTH['key']}': (" {project_name}/settings.py""")
    



if __name__ == '__main__':
    shell = SetupDrfSeed()
    # shell._create_virtualenv()
    # shell._install_dependencies(shell._args.proxy)
    print(shell._args)
    shell._set_router(shell._args.project_name, shell._args.router)
    shell._set_auth_classes(shell._args.project_name, shell._args.auth)
    shell._set_pagination(shell._args.project_name, shell._args.pagination, shell._args.page_size)
    shell._set_throttling(shell._args.project_name, shell._args.throttling)