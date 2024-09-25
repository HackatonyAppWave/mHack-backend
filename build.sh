set -o errexit

pip install -r core/requirements.txt

# Convert static asset files
python core/manage.py collectstatic --no-input

# Apply any outstanding database migrations
python core/manage.py migrate
