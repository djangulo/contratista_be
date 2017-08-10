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
    - Any combination of: `anon`, `user`, `scoped` followed by the rate as  `{rate}/{second,minute,hour,day,month,year}`.
    - Any argument not named `anon` or `user` will be considered a `scoped` variation.
    - Add an empty argument for scoped to add it to the default classes, otherwise, you'll need to add the scoped class on a per-view basis:

            # python
            from rest_framework.throttling import ScopedRateThrottle
            from rest_frameworkviews import APIView

            class MyViewSet(APIView):
                throttle_classes = (ScopedRateThrottle,)
                throttle_scope = 'authtoken'
                ...

    - Example:

            python setup.py my_project --throttling anon=1000/day scoped user=1000/hour contacts=1000/day uploads=10/minute
 
 - `--static-root`
    - Configures `STATIC_ROOT` in `settings.py` to whatever arguments is passed.
    - If called without argument, will default to `static` folder in the root dir.
 - `--static-url`
    - Configures `STATIC_URL` in `settings.py` to whatever argument is passed.
    - If called without argument, will default to `/static/` url.

- `--media-root`
    - Configures `MEDIA_ROOT` in `settings.py` to whatever argument is passed; to `media` folder in root dir
    - This is necessary if you intend to work with and display images.

- `--media-url`
    - Configures `MEDIA_URL` in `settings.py` to whatever argument is passed.
    - If no argument is passed, will default to `/media/` url.
    - If set, also configures `urls.py` to display media.
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

 - Configure `settings.REST_FRAMEWORK` to taste




