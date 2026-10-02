#!/usr/bin/env bash
# Render build script — exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Optional auto-create superuser on Render.
# Set these 3 env vars in Render dashboard to enable:
# DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring superuser $DJANGO_SUPERUSER_USERNAME exists..."
  python manage.py createsuperuser --noinput || true
  python manage.py shell -c "import os; from accounts.models import CustomUser; u=CustomUser.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).first(); print('updating password...' if u else 'creating via update_or_create...'); u, _=CustomUser.objects.update_or_create(username=os.environ.get('DJANGO_SUPERUSER_USERNAME'), defaults={'email': os.environ.get('DJANGO_SUPERUSER_EMAIL'), 'is_superuser': True, 'is_staff': True}); u.set_password(os.environ.get('DJANGO_SUPERUSER_PASSWORD')); u.save(); print('superuser ready: ' + u.username)"
fi
