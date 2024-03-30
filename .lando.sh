#!/bin/sh

env
su www-data -c "poetry run ./manage.py runserver 0.0.0.0:80"
