import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_name = "posts_post" AND column_name = "category"')
print('Exists:', cursor.fetchone() is not None)
