import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT schema_name FROM information_schema.schemata')
schemas = [r[0] for r in cursor.fetchall()]
print('Schemas:', schemas)
cursor.execute('SHOW search_path')
print('Search path:', cursor.fetchone())
