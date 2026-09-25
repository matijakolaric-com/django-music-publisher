release: python manage.py migrate
postdeploy: python manage.py migrate
web: waitress-serve --port=$PORT dmp_project.wsgi:application
