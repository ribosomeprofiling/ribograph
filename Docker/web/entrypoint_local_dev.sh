#!/bin/bash

cd ribograph
# reflect any model changes to the database.
python manage.py makemigrations
python manage.py migrate

# This makes it possible to create and modify files from the host machine
umask 0000


# we need to run npm development env for development.
npm install
nohup npm run dev &


exec "$@"

