# drf-seed: Django Rest Framework seed project

Starter seed for a Django Rest Framework RESTful API; initially configured for development.

It contains the following:

 - Built in `accounts` app:
   - Custom user with email/username
   - Automatic [Token](http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication) creation on user creation. To disable, remove or comment out lines 15 through 18 on `accounts/models.py`.
   - `UserSerializer`: serializer for the custom user model. Email field is `write_only` by default.
   - `UserViewSet`: viewset with `retrieve`, `update`, `destroy`, `list` methods. Registered under `accounts` on the `DefaultRouter`.
   - `RegisterUserViewSet`: with custom `create` method, as registration is usually handled separately (and permission free `post` requests). Registered under `register` on the `DefaultRouter`.
   - `ThrottledObtainToken` and `throttled_obtain_token` class and view, respectively: throttled version of DRF's standard `obtain_auth_token` view.
   - `AllowPostFromUnregisteredUser` permission, self explanatory. Used for registering unauthenticated users.
   - `IsOwnerOrReadOnly` permission, object level permission.


This project depends on (as of 8/4/2017):

 - [git](https://git-scm.com/) - Version control and dependency management
 - [python 3](http://python.org/) - Global install to make virtualenv
 - [django](https://www.djangoproject.com/) - High level Python Web Framework
 - [django-rest-framework](http://www.django-rest-framework.org/) - core RESTful API framework
 - [django-cors-headers](https://github.com/ottoyiu/django-cors-headers) - Allows simple CORS operations

## Installation

### Scripted

For a manual installation, go to [manual install](#manual-install)

Clone the repo and run the install.py script

    git clone https://github.com/djangulo/drf_seed.git my_project
    python setup.py my_project

The install.py script can be run with the optional arguments below. Most arguments (except `project-name`) carry a default value which you can later override.

 - `project-name`
    
    Name for the DRF project. Positional and must be first. Required.

 - `--proxy`
    - If you're behind a proxy, this will tell `pip` to use these credentials when downloading
    - Use as follows: `--proxy user:password@address:port`
    - Example:

        `python setup.py my_project --proxy djangulo:hunter2@proxy-address:1234`

        when the script calls pip, it will run:

        `pip --proxy djangulo:hunter2@proxy-address:1234 install bar foo foo-bar`

 - `--auth`
    - Default authentication class(es) for `DEFAULT_AUTHENTICATION_CLASSES` in `settings.py`
    - Options:  any combination of `basic`, `token`, `session`.
    - Will be added in the order provided

 - `--router`
    - Router to use, if any.
    - Options: `simple`, `default`, `none`
    - Defaults to `default`, `none` removes the router from `my_project/urls.py`

 - `---pagination`
    - Default pagination class for `DEFAULT_PAGINATION_CLASS` in `settings.py`
    - options: `page`, `limitoffset`, `cursor`, `none`
    - Defaults to `page`

 - `--page-size`
    - Integer to set page size, ignored if `--pagination` is not set.
    - If `--default-pagination` is provided, defaults to 20.

 - `--throttling`
    - Default throttle class(es) for `DEFAULT_THROTTLE_CLASSES` in `settings.py`
    - Any combination of: `anon`, `user`, or `scoped` followed by the rate as  `{rate}/{second,minute,hour,day,month,year}`.
    - Any argument not named `anon` or `user` will be considered `scoped`.
    - Keep in mind scoped throttle rates need to be set on a per-view basis:

            # python
            from rest_framework.throttling import ScopedRateThrottle
            from rest_frameworkviews import APIView

            class MyViewSet(APIView):
                throttle_classes = (ScopedRateThrottle,)
                throttle_scope = 'authtoken'
                ...

    - Example:

            python setup.py my_project --throttling anon=1000/day user=1000/hour contacts=1000/day uploads=10/minute
 
 - `--static`
    - Configures `STATIC_ROOT` and `STATIC_URL` in `settings.py` to whatever argument is passed.
    - If called without argument, will default to `static` folder in the root dir.

- `--media-root`
    - Configures `MEDIA_ROOT` in `settings.py` to whatever argument is passed; to `media` folder in root dir
    - Will be setup automatically if `--media-url` is set without a media-root.
    - Will add a media outlet url to `my_project/urlpatterns.py`.
    - This is necessary if you intend to work with and display images.

- `--media-url`
    - Configures `MEDIA_URL` in `settings.py` to whatever argument is passed.
    - If no argument is passed, will default to 'media' folder in root dir.
    - Will be setup automatically if `--media-root` is set without a media-url.
    - Will add a media outlet url to `my_project/urlpatterns.py`.
    - This is necessary if you intend to work with and display images.

### Manual install

Run the steps the `setup.py` script would follow manually:

Note some of the sed operations are inserting text down-top (as opposed to top-down, how we normally write)

 - Clone the repo

        git clone https://github.com/djangulo/drf_seed.git my_project

 - Create a virtualenv and activate it

        python -m venv virtualenv && source virtualenv/bin/activate

 - Install requirements.txt using pip

        pip install -r requirements.txt

 - Configure, all of which are obviously optional:

    I'm a big fan of sed, although it can get unwieldy for some longer commands. I would suggest creating an environment variable for the project name, as it will be extensively used from here onward:

        PROJECT_NAME=my_project`

    Rename all instances of `drf_seed` to your projects name (`my_project` on the following examples)

        sed -i s:drf_seed:$PROJECT_NAME:g drf_seed/* && mv drf_seed $PROJECT_NAME
        sed -i s:drf_seed:$PROJECT_NAME:g manage.py

    Set the API url prefix

        sed -i "s:(r':(r'my-prefix/my-version/:g" my_project/urls.py

    Set default authentication class(es):

       sed "/REST_FRAMEWORK/a\    )," $PROJECT_NAME/settings.py \
       | sed "/REST_FRAMEWORK/a\        'rest_framework.authentication.TokenAuthentication'," \
       | sed "/REST_FRAMEWORK/a\    'DEFAULT_AUTHENTICATION_CLASSES': (," \
       | tee $PROJECT_NAME/settings.py

    `sed -i "/REST_FRAMEWORK/a\    )," $PROJECT_NAME/settings.py`

    `sed -i "/REST_FRAMEWORK/a\        'rest_framework.authentication.TokenAuthentication'," my_project/settings.py`

    `sed -i "/REST_FRAMEWORK/a\        'rest_framework.authentication.SessionAuthentication'," my_project/settings.py`

    `sed -i "/REST_FRAMEWORK/a\    'DEFAULT_AUTHENTICATION_CLASSES': (," my_project/settings.py`




