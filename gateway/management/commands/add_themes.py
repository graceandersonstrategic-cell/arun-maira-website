# gateway/management/commands/add_themes.py
from django.core.management.base import BaseCommand
from gateway.models import Theme

class Command(BaseCommand):
    help = 'Adds the default reading ideas themes'
    
    def handle(self, *args, **options):
        themes_data = [
            # The System (Bucket 1)
            {
                'name': 'Complex Systems: Social Change',
                'slug': 'complex-systems-social-change',
                'bucket': 'system',
                'order': 1,
                'description': 'Understanding how social change happens in complex systems'
            },
            {
                'name': 'Democracy and Public Policy',
                'slug': 'democracy-public-policy',
                'bucket': 'system',
                'order': 2,
                'description': 'Exploring democratic processes and public policy making'
            },
            {
                'name': 'Evolution of Economics',
                'slug': 'evolution-economics',
                'bucket': 'system',
                'order': 3,
                'description': 'How economic thought and systems have evolved'
            },
            {
                'name': 'Jobs and Employment',
                'slug': 'jobs-employment',
                'bucket': 'system',
                'order': 4,
                'description': 'The future of work, employment, and livelihoods'
            },
            {
                'name': 'Business Ethics',
                'slug': 'business-ethics',
                'bucket': 'system',
                'order': 5,
                'description': 'Ethical considerations in business and commerce'
            },
            
            # Me/Us (Bucket 2)
            {
                'name': 'Purpose of Our Lives',
                'slug': 'purpose-our-lives',
                'bucket': 'me_us',
                'order': 1,
                'description': 'Finding meaning and purpose in life'
            },
            {
                'name': 'Listening to Others',
                'slug': 'listening-others',
                'bucket': 'me_us',
                'order': 2,
                'description': 'The art and importance of listening'
            },
            
            # Future of India (Bucket 3)
            {
                'name': 'Future of India',
                'slug': 'future-india',
                'bucket': 'future_india',
                'order': 1,
                'description': 'Vision and pathways for India\'s development'
            },
        ]
        
        created_count = 0
        for theme_data in themes_data:
            theme, created = Theme.objects.get_or_create(
                slug=theme_data['slug'],
                defaults=theme_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Added theme: {theme_data["name"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Theme already exists: {theme_data["name"]}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added {created_count} themes')
        )