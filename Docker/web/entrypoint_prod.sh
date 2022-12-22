#!/bin/sh

python manage.py migrate
python manage.py collectstatic --no-input --clear


npm install
npm run build 

exec "$@"
