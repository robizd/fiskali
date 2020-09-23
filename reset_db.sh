#!/bin/sh

set -e  # Exit immediately if a simple command exits with a nonzero exit value
dropdb fiskalna
createdb fiskalna

rm -f hr/migrations/[0-9]*.*
rm -f media/*.*

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata user
