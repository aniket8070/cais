import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cais.settings')
import django
django.setup()
from django.contrib.auth.models import User
User.objects.filter(username='admin').delete()
u = User.objects.create_superuser('admin', 'admin@cais.com', 'Admin@1234')
print('Created:', u.username)