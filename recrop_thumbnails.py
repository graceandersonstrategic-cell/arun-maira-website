import os, sys, re, requests
from io import BytesIO

sys.path.insert(0, '/home/arungkci/arun_maira_site')
os.environ['DJANGO_SETTINGS_MODULE'] = 'arun_gateway.settings'
import django
django.setup()

from PIL import Image
from gateway.models import Talk
from django.conf import settings

def get_video_id(url):
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url or '')
    return match.group(1) if match else None

headers = {'User-Agent': 'Mozilla/5.0'}

for talk in Talk.objects.all():
    vid = get_video_id(talk.external_link)
    if not vid:
        continue

    thumb_path = f'talks/thumbnails/{vid}.jpg'
    full_path = os.path.join(settings.MEDIA_ROOT, thumb_path)

    for quality in ['maxresdefault', 'hqdefault']:
        url = f'https://img.youtube.com/vi/{vid}/{quality}.jpg'
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content))
                w, h = img.size
                # Crop 22% from top and 18% from bottom
                top = int(h * 0.22)
                bottom = int(h * 0.18)
                cropped = img.crop((0, top, w, h - bottom))
                final = cropped.resize((640, 360), Image.LANCZOS)
                final.save(full_path, 'JPEG', quality=90)
                print(f'Re-cropped ({quality}): {talk.title}')
                break
        except Exception as e:
            print(f'Error: {e}')

print('All done!')
