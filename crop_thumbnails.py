import os
import sys
import re
import requests
from io import BytesIO

sys.path.insert(0, '/home/arungkci/arun_maira_site')
os.environ['DJANGO_SETTINGS_MODULE'] = 'arun_gateway.settings'

import django
django.setup()

from PIL import Image
from gateway.models import Talk
from django.conf import settings

thumb_dir = os.path.join(settings.MEDIA_ROOT, 'talks/thumbnails')
os.makedirs(thumb_dir, exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0'}

def get_video_id(url):
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url or '')
    return match.group(1) if match else None

for talk in Talk.objects.all():
    vid = get_video_id(talk.external_link)
    if not vid:
        print(f'No video ID: {talk.title}')
        continue

    thumb_path = f'talks/thumbnails/{vid}.jpg'
    full_path = os.path.join(settings.MEDIA_ROOT, thumb_path)

    if not os.path.exists(full_path):
        for quality in ['maxresdefault', 'hqdefault']:
            url = f'https://img.youtube.com/vi/{vid}/{quality}.jpg'
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    img = Image.open(BytesIO(r.content))
                    w, h = img.size
                    crop_h = int(h * 0.12)
                    cropped = img.crop((0, crop_h, w, h - crop_h))
                    final = cropped.resize((640, 360), Image.LANCZOS)
                    final.save(full_path, 'JPEG', quality=85)
                    print(f'Saved ({quality}): {talk.title}')
                    break
            except Exception as e:
                print(f'Error downloading: {e}')
    else:
        print(f'Already exists: {talk.title}')

    # Update thumbnail in DB only
    Talk.objects.filter(pk=talk.pk).update(thumbnail=thumb_path)

print('\nAll done!')
