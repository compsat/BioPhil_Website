#!/bin/bash

# Make database migrations
echo "Create the Database Migrations"
python3 bio_phil/manage.py makemigrations

# Apply database migrations
echo "Apply databse"
python3 bio_phil/manage.py migrate

echo "Starting server"
python3 bio_phil/manage.py runserver 0.0.0.0:8000