import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.test import Client
from posts.services import PostService

client = Client()

# Simulate AJAX POST to /generate/
response = client.post('/generate/', {
    'topic': 'Aquarius',
    'custom_topic': 'Aquarius',
}, HTTP_X_REQUESTED_WITH='XMLHttpRequest', HTTP_ACCEPT='application/json')

print("Status:", response.status_code)
print("Content:", response.content.decode('utf-8')[:500])
