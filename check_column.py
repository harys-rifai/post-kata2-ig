import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position', ['public', 'posts_post'])
cols = [r[0] for r in cursor.fetchall()]
print('Columns:', cols)
print('Has category:', 'category' in cols)
