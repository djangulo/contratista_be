import argparse
import os
import sys

from subprocess import Popen, PIPE, run
from random import SystemRandom

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def __run__(*args, **kwargs):
    return run(*args, **kwargs, shell=True)

class SetupDrfSeed:
    """Sets up the drf_seed project, along with some settings in
    urls.py and settings.py"""
    def __init__(self):
        self._sanity_checks()
        self._parse_arguments()
        self._import_settings(self._args.project_name)
    
    def _import_settings(self, proj):
        """Utility method to provide a project/settings.py handle and a
        settings.REST_FRAMEWORK handle"""
        self.project_name = proj
        self._rename_drf_seed_instances()
        self.settings_str = f'{self.project_name}/settings.py'
        try:
            self.settings = __import__(
                f'{self.project_name}.settings',
                globals(),
                locals(),
                ['*']
            )
            self.drf_settings = self.settings.REST_FRAMEWORK
        except ModuleNotFoundError:
            sys.exit(f'Could not locate {self.project_name}/settings.py, was '
                    'this script run from the root dir?')

    def _sanity_checks(self):
        """Checks that requirements are installed and determines the
        python cli command to invoke"""
        try:
            outs, errs = Popen('sed --version', stdout=PIPE, shell=True).communicate(timeout=5)
        except FileNotFoundError:
            sys.exit('ERROR: sed is not installed or is not found in $PATH')
        try:
            outs, errs = Popen('git --version', stdout=PIPE, shell=True).communicate(timeout=5)
        except FileNotFoundError:
            sys.exit('ERROR: git is not installed or is not found in $PATH')
        try:
            outs, errs = Popen('python3.6 --version', stdout=PIPE, shell=True).communicate(timeout=5)
            self.python_caller = 'python3.6'
        except FileNotFoundError:
            try:
                outs, errs = Popen('python3 --version', stdout=PIPE, shell=True).communicate(timeout=5)
                if '3.6' in str(outs):
                    self.python_caller = 'python3'
                else:
                    sys.exit('This script only compatible with python >= 3.6.1')
            except FileNotFoundError:
                try:
                    outs, errs = Popen('python --version', stdout=PIPE, shell=True).communicate(timeout=5)
                    if '3.6' in str(outs):
                        self.python_caller = 'python'
                    else:
                        sys.exit('This script only compatible with python >= 3.6.1')
                except FileNotFoundError:
                    sys.exit('ERROR: python is not installed or is not found in $PATH')

    def _parse_arguments(self):
        """Argument parsing"""
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
            help='Sets DEFAULTTHROTTLE_CLASSES in settings.py')
        parser.add_argument('--static-root', action='store', type=str, nargs='?',
            const='static')
        parser.add_argument('--static-url', action='store', type=str, nargs='?',
            const='static')
        parser.add_argument('--media-root', action='store', type=str, nargs='?',
            const='media')
        parser.add_argument('--media-url', action='store', type=str, nargs='?',
            const='media')
        self._args = parser.parse_args()

    def _create_virtualenv(self):
        """Creates virtualenv under the ~/project/virtualenv/ 
        directory by calling python -m venv virtualenv"""
        if 'virtualenv' not in os.listdir(BASE_DIR):
            if 'win' in sys.platform:
                command = f'{self.python_caller} -m venv {BASE_DIR}\\virtualenv'
                __run__(command, stdout=PIPE)
            else:
                command = f'{self.python_caller} -m venv {BASE_DIR}/virtualenv'
                __run__(command, stdout=PIPE)

    def _install_dependencies(self, proxy=None):
        """Installs 'requirements.txt using pip"""
        if 'win' in sys.platform:
            command = f'{BASE_DIR}\\virtualenv\\Scripts\\pip '
            command += f"--proxy {proxy  + ' ' if proxy else ''}"
            command += f'install -r {BASE_DIR}\\requirements.txt'
            __run__(command)
        else:
            command = f'{BASE_DIR}/virtualenv/bin/pip '
            command += f"--proxy {proxy + ' ' if proxy else ''}"
            command += f'install -r {BASE_DIR}/requirements.txt'
            __run__(command)

    def _rename_drf_seed_instances(self):
        """Renames project's generic name with your own"""
        if 'drf_seed' in os.listdir(BASE_DIR):
            __run__(f'sed -i s:drf_seed:{self.project_name}:g drf_seed/*')
            __run__(f'mv drf_seed {self.project_name}')

    def _set_router(self, router=None):
        """Sets default router to use, if any"""
        _ROUTERS = {
            'simple': 'SimpleRouter',
            'default': 'DefaultRouter',
            'none': None,
        }
        if router:
            if router == 'none':
                __run__(f'''sed -i "/router/d" {self.project_name}/urls.py''')
            else:
                __run__(f'''sed -i "s:DefaultRouter:{_ROUTERS[router]}:g" {self.project_name}/urls.py''')

    def _set_auth_classes(self, auth_classes=None):
        """Sets Authentication classes to use in settings.py"""
        A = {
            'key': 'DEFAULT_AUTHENTICATION_CLASSES',
            'token': 'rest_framework.authentication.TokenAuthentication',
            'session': 'rest_framework.authentication.SessionAuthentication',
            'basic': 'rest_framework.authentication.BasicAuthentication',
        }
        if auth_classes:
            try:
                DRF = self.drf_settings
                if A['key'] in DRF.keys():
                    print(f"{A['key']} exists, and contains: ")
                    for v in DRF[A['key']]:
                        print('\t' + v)
                    print('\t Skipping, override manually')
                else:
                    raise KeyError(f"{A['key']} not found, creating...")
            except KeyError:
                __run__(f"sed -i '/REST_FRAMEWORK/a\    ),' {self.settings_str}")
                for a in auth_classes:
                    __run__(f"""sed -i "/REST_FRAMEWORK/a\        '{A[a]}'," {self.settings_str}""")
                __run__(f"""sed -i "/REST_FRAMEWORK/a\    '{A['key']}': (" {self.settings_str}""")

    def _set_pagination(self, pag=None, size=20):
        """Sets pagination class in settings.py"""
        P = {
            'key': 'DEFAULT_PAGINATION_CLASS',
            'size_key': 'PAGE_SIZE',
            'page': 'rest_framework.pagination.PageNumberPagination',
            'limitoffset': 'rest_framework.pagination.LimitOffsetPagination',
            'cursor': 'rest_framework.pagination.CursorPagination',
        }
        if pag:
            if pag == 'none':
                __run__(f'''sed -i "/{P['key']}/d" {self.settings_str}''')
                __run__(f'''sed -i "/{P['size_key']}/d" {self.settings_str}''')
            else:
                try:
                    DRF = self.drf_settings
                    if P['key'] in DRF.keys():
                        pag_val = DRF[P['key']]
                        size_val = DRF[P['size_key']]
                        print(f"{P['key']} exists, its value is: {pag_val}, with size {size_val} ")
                        print(f'Replacing {pag_val} with {P[pag]}')
                        print(f"Replacing {P['size_key']}: {size_val} with {P['size_key']}: {size}")
                        __run__(f'''sed -i "s/{pag_val}/{P[pag]}/g" {self.settings_str}''')
                        __run__(f'''sed -i "s/'{P['size_key']}': {size_val},/'{P['size_key']}': {size},/g" {self.settings_str}''')
                    else:
                        raise KeyError(f"{P['key']} not found, creating...")
                except KeyError:
                    __run__(f"""sed -i "/REST_FRAMEWORK/a\    '{P['key']}': '{P[pag]}'," {self.settings_str}""")
                    __run__(f'''sed -i "/{P['key']}/a\    '{P['size_key']}': {size}," {self.settings_str}''')


    def _set_throttling(self, classes=None):
        """Sets throttling classes and rates in settings.py"""
        T = {
            'classes': 'DEFAULT_THROTTLE_CLASSES',
            'rates': 'DEFAULT_THROTTLE_RATES',
            'anon': 'rest_framework.throttling.AnonRateThrottle',
            'user': 'rest_framework.throttling.UserRateThrottle',
            'scoped': 'rest_framework.throttling.ScopedRateThrottle',
        }
        if classes:
            # build scopes dict = {'anon': '1000/day', 'user': '1000/day', ...}
            scopes = {
                s.split('=')[0]: s.split('=')[1].replace('/','/') if '=' in s else s for s in classes
            }
            scopes['authtoken'] = '10/minute'
            try:
                DRF = self.drf_settings
                if T['classes'] in DRF.keys():
                    print(f"{T['classes']} exists, contains:")
                    for c in DRF[T['classes']]:
                        print(f"\t {c}")
                    for s in scopes.keys():
                        cond1 = s in ('anon', 'user', 'scoped')
                        if cond1:
                            cond2 = T[s] not in DRF[T['classes']]
                        if cond2:
                            __run__(f'''sed -i "{T['classes']}/a\        {T[s]}," {self.settings_str}''')
                else:
                    raise KeyError(f"{T['classes']} not found, creating...")
            except KeyError:
                __run__(f"sed -i '/REST_FRAMEWORK/a\    ),' {self.settings_str}")
                for s in scopes.keys():
                    if s in ('anon', 'user', 'scoped'):
                        __run__(f"""sed -i "/REST_FRAMEWORK/a\        '{T[s]}'," {self.settings_str}""")
                __run__(f"""sed -i "/REST_FRAMEWORK/a\    '{T['classes']}': (" {self.settings_str}""")
            try:
                if T['rates'] in DRF.keys():
                    print(f"{T['rates']} exists, contains:")
                    for r in DRF[T['rates']]:
                        print(f"\t{r}")
                        for k, v in scopes.items():
                            cond1 = k != 'scoped'
                            cond2 = k not in DRF[T['rates']].keys()
                            if cond1 and cond2:
                                __run__(f"""sed -i "/{T["rates"]}/a\        '{k}': '{v}'," {self.settings_str}""")
                else:
                    raise KeyError(f"{T['rates']} not found, creating...")
            except KeyError:
                __run__(f"sed -i '/REST_FRAMEWORK/a\    }},' {self.settings_str}")
                for k, v in scopes.items():
                    if k != 'scoped':
                        __run__(f"""sed -i "/REST_FRAMEWORK/a\        '{k}': '{v}'," {self.settings_str}""")
                __run__(f"""sed -i "/REST_FRAMEWORK/a\    '{T['rates']}': {{" {self.settings_str}""")
    
    def _set_static_root(self, dir_name):
        hook = 'REST_FRAMEWORK'
        if dir_name:
            if hasattr(self.settings, 'STATIC_ROOT'):
                print(f'STATIC_ROOT exists, replacing value to {dir_name}')
                __run__(f'''sed -i "/STATIC_ROOT/d" {self.settings_str}''')
                __run__(f'''sed -i "/{hook}/i\STATIC_ROOT = os.path.join(BASE_DIR, '{dir_name}')" {self.settings_str}''')
            else:
                print(f'STATIC_ROOT not found, creating...')
                __run__(f'''sed -i "/{hook}/i\STATIC_ROOT = os.path.join(BASE_DIR, '{dir_name}')" {self.settings_str}''')

    def _set_static_url(self, url_name):
        hook = 'REST_FRAMEWORK'
        if url_name:
            if hasattr(self.settings, 'STATIC_URL'):
                print(f'STATIC_URL exists, replacing value to {url_name}')
                __run__(f'''sed -i "/STATIC_URL/d" {self.settings_str}''')
                __run__(f'''sed -i "/{hook}/i\STATIC_URL= '/{url_name}/'" {self.settings_str}''')
            else:
                print(f'STATIC_URL not found, creating...')
                __run__(f'''sed -i "/{hook}/i\STATIC_URL = '/{url_name}/'" {self.settings_str}''')

    def _set_media_root(self, dir_name):
        hook = 'REST_FRAMEWORK'
        if dir_name:
            if hasattr(self.settings, 'MEDIA_ROOT'):
                print(f'MEDIA_ROOT exists, replacing value to {dir_name}')
                __run__(f'''sed -i "/MEDIA_ROOT/d" {self.settings_str}''')
                __run__(f'''sed -i "/{hook}/i\MEDIA_ROOT = os.path.join(BASE_DIR, '{dir_name}')" {self.settings_str}''')
            else:
                print(f'MEDIA_ROOT not found, creating...')
                __run__(f'''sed -i "/{hook}/i\MEDIA_ROOT = os.path.join(BASE_DIR, '{dir_name}')" {self.settings_str}''')

    def _set_media_url(self, url_name):
        hook = 'REST_FRAMEWORK'
        if url_name:
            if hasattr(self.settings, 'MEDIA_URL'):
                print(f'MEDIA_URL exists, replacing value to {url_name}')
                __run__(f'''sed -i "/MEDIA_URL/d" {self.settings_str}''')
                __run__(f'''sed -i "/{hook}/i\MEDIA_URL= '/{url_name}/'" {self.settings_str}''')
            else:
                print(f'MEDIA_URL not found, creating...')
                __run__(f'''sed -i "/{hook}/i\MEDIA_URL = '/{url_name}/'" {self.settings_str}''')
            __run__(f'''sed -i "/import settings/d" {self.project_name}/urls.py''')
            __run__(f'''sed -i "/import static/d" {self.project_name}/urls.py''')
            __run__(f'''sed -i "/from django.conf.urls/i\\from django.conf import settings" {self.project_name}/urls.py''')
            __run__(f'''sed -i "/from django.conf.urls/a\\from django.conf.urls.static import static" {self.project_name}/urls.py''')
            __run__(f'''sed -i "/static(settings.MEDIA_URL,/d" {self.project_name}/urls.py''')
            #__run__(r'''sed -i "$a\urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)" {name}/urls.py'''.format(name=self.project_name))

    def _create_and_set_secret_key(self):
        secret_key_file = os.path.join(BASE_DIR, self.project_name, 'secret_key.py')
        if not secret_key_file in os.listdir(os.path.join(BASE_DIR, self.project_name)):
            chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            key = ''.join(systemRandom().choice(chars) for _ in range(50))
            with open(secret_key_file, 'w') as fn:
                fn.write(f'SECRET_KEY = "{key}""')
        __run__(f'''sed -i "s/SECRET_KEY = ''/#SECRET_KEY = ''/g" {self.settings_str}''')
        __run__(f'''sed -i "/import os/a\\from .secret_key import SECRET_KEY''')


if __name__ == '__main__':
    s = SetupDrfSeed()
    s._create_virtualenv()
    s._install_dependencies(s._args.proxy)
    s._set_router(s._args.router)
    s._set_auth_classes(s._args.auth)
    s._set_pagination(s._args.pagination, s._args.page_size)
    s._set_throttling(s._args.throttling)
    s._set_static_root(s._args.static_root)
    s._set_static_url(s._args.static_url)
    s._set_media_root(s._args.media_root)
    s._set_media_url(s._args.media_url)
    s._create_and_set_secret_key()