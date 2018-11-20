#!/bin/bash

# Make database migrations
echo "Create the Database Migrations"
python3 bio_phil/manage.py makemigrations

# Apply database migrations
echo "Apply database"
python3 bio_phil/manage.py migrate

echo "Run Fixtures"
python3 bio_phil/manage.py loaddata modules.yaml
python3 bio_phil/manage.py loaddata module_images.yaml

echo "Create superuser"
python bio_phil/manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='bio_phil@gmail.com'):
    User.objects.create_superuser('bio_phil@gmail.com', 'bioisfun')
END

echo "Starting server"
python3 bio_phil/manage.py runserver 0.0.0.0:8000
