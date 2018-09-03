# Apply database migrations
echo "Create the database migrations"
python3 bio_phil/manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python3 bio_phil/manage.py migrate

echo "Create superuser"
python bio_phil/manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='bio_phil@gmail.com'):
    User.objects.create_superuser('bio_phil@gmail.com', 'bioisfun')
END

# Start Server
echo "Starting Server"
python3 bio_phil/manage.py runserver 0.0.0.0:8000