import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE %s', ['%post%'])
for row in cursor.fetchall():
    print(row)
