# Apply database migrations
echo "Create the database migrations"
python3 bio_phil/manage.py makemigrations

# Apply database migrations
echo "Apply database migrations"
python3 bio_phil/manage.py migrate

# Start Server
echo "Starting Server"
python3 bio_phil/manage.py runserver 0.0.0.0:8000