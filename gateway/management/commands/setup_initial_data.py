from django.core.management.base import BaseCommand
from gateway.models import GatewayPage, Theme, SocialMediaProfile, Book
from gateway.models import GatewayPage, Theme, SocialMediaProfile, Book, Article

class Command(BaseCommand):
    help = 'Sets up initial gateway pages, themes, social media profiles, and sample books'

    def handle(self, *args, **options):
        # Create default pages
        pages = [
            {
                'page_type': 'home',
                'title': 'A Quiet Space for Thoughtful Inquiry',
                'content': '''
                    <p>Welcome. This space is intended as a gateway to the work of Arun Maira—writer, former planner, and independent thinker focused on systemic change, governance, and the human dimensions of economics.</p>
                    
                    <p>Here you will find an overview of his published books, the principal themes that shape his writing, and a quiet pathway into his deeper body of work. The intention is not to host conversation, but to offer a clear, respectful entry point for those encountering his ideas for the first time.</p>
                    
                    <p>For those already familiar with his writing, the reading and listening rooms remain exactly as they have always been—undisturbed archives of essays, articles, and talks, organized thematically and without commentary.</p>
                '''
            },
            {
                'page_type': 'about',
                'title': 'About Arun Maira',
                'content': '''
                    <p>Arun Maira is a writer and former planner whose work focuses on systemic change, governance, and the human dimensions of economics. His career has spanned corporate leadership, policy advising, and independent inquiry.</p>
                    
                    <p>After studying physics at St. Stephen's College, Delhi, and engineering at the Indian Institute of Technology, Delhi, Arun spent twenty-four years with the Tata Group, where he served on the board of Tata Motors and led several of the Group's companies. He later chaired the Boston Consulting Group in India and served as a member of the Planning Commission of India, where he focused on industrial and infrastructure policy.</p>
                    
                    <p>In recent years, he has stepped back from institutional roles to write and think independently. His books explore the intersection of systems thinking, governance, equity, and the care economy. He writes regularly for academic, policy, and public audiences, and speaks at institutions around the world.</p>
                    
                    <p>His website is conceived not as a public platform for conversation, but as a quiet reading room for those who wish to engage with his ideas in depth, at their own pace, and without the noise of social commentary.</p>
                '''
            },
            {
                'page_type': 'books',
                'title': 'Books',
                'content': '<p>Published works spanning systems thinking, governance, and economic reimagining.</p>'
            },
            {
                'page_type': 'themes',
                'title': 'Thematic Pathways',
                'content': '<p>Entry points into the reading room of ideas.</p>'
            },
            {
                'page_type': 'media',
                'title': 'Media & Press',
                'content': '<p>For journalists, academics, and institutions seeking background material.</p>'
            },
            {
                'page_type': 'contact',
                'title': 'Contact',
                'content': '<p>For institutions, editors, event organizers, and serious readers.</p>'
            },
            {
                'page_type': 'connect',
                'title': 'Connect',
                'content': '<p>Quiet ways to follow the work.</p>'
            },
        ]
        
        for page_data in pages:
            GatewayPage.objects.update_or_create(
                page_type=page_data['page_type'],
                defaults={
                    'title': page_data['title'],
                    'content': page_data['content']
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Created/updated {page_data['page_type']} page"))
        
        # Create Arun's themes according to his three-bucket structure
        themes = [
            # The System bucket
            {
                'name': 'Complex Systems: Social Change',
                'slug': 'complex-systems-social-change',
                'description': 'Understanding complex systems and their dynamics in social transformation',
                'bucket': 'system',
                'order': 0,
            },
            {
                'name': 'Democracy and Public Policy',
                'slug': 'democracy-public-policy',
                'description': 'Governance, democratic processes, and policy design',
                'bucket': 'system',
                'order': 1,
            },
            {
                'name': 'Evolution of Economics',
                'slug': 'evolution-of-economics',
                'description': 'How economic thinking and systems have evolved',
                'bucket': 'system',
                'order': 2,
            },
            {
                'name': 'Jobs and Employment',
                'slug': 'jobs-employment',
                'description': 'Work, livelihoods, and economic participation',
                'bucket': 'system',
                'order': 3,
            },
            {
                'name': 'Business Ethics',
                'slug': 'business-ethics',
                'description': 'Ethical dimensions of business and organizational life',
                'bucket': 'system',
                'order': 4,
            },
            
            # Me/Us bucket
            {
                'name': 'Purpose of Our Lives',
                'slug': 'purpose-of-our-lives',
                'description': 'Meaning, purpose, and personal fulfillment',
                'bucket': 'me_us',
                'order': 0,
            },
            {
                'name': 'Listening to Others',
                'slug': 'listening-to-others',
                'description': 'Communication, understanding, and human connection',
                'bucket': 'me_us',
                'order': 1,
            },
            
            # Future of India bucket
            {
                'name': 'Future of India',
                'slug': 'future-of-india',
                'description': 'India\'s development path and future possibilities',
                'bucket': 'future_india',
                'order': 0,
            },
        ]
        
        for theme_data in themes:
            Theme.objects.update_or_create(
                slug=theme_data['slug'],
                defaults={
                    'name': theme_data['name'],
                    'description': theme_data['description'],
                    'bucket': theme_data['bucket'],
                    'order': theme_data['order']
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Created/updated theme: {theme_data['name']} ({theme_data['bucket']})"))
        
        # Create social media profiles (updated per Arun's email)
        social_profiles = [
            {
                'platform': 'linkedin',
                'profile_url': 'https://www.linkedin.com/in/arun-maira-profile/',
                'display_text': 'LinkedIn (primary platform)',
                'icon_name': 'linkedin-in',
                'order': 0,
                'show_in_footer': True,
                'show_in_sidebar': True,
            },
            {
                'platform': 'twitter',
                'profile_url': 'https://twitter.com/ArunMaira',
                'display_text': 'Twitter (not actively used)',
                'icon_name': 'twitter',
                'order': 1,
                'show_in_footer': False,
                'show_in_sidebar': False,
                'is_active': False,  # Mark as inactive since not used
            },
            {
                'platform': 'newsletter',
                'profile_url': '/contact#newsletter',
                'display_text': 'Quiet Email List',
                'icon_name': 'envelope',
                'order': 2,
                'show_in_footer': True,
                'show_in_sidebar': True,
            },
            {
                'platform': 'goodreads',
                'profile_url': 'https://www.goodreads.com/author/show/XXXXX',
                'display_text': 'Goodreads',
                'icon_name': 'goodreads-g',
                'order': 3,
                'show_in_footer': True,
                'show_in_sidebar': False,
            },
            {
                'platform': 'amazon',
                'profile_url': 'https://www.amazon.com/author/arunmaira',
                'display_text': 'Amazon Author Page',
                'icon_name': 'amazon',
                'order': 4,
                'show_in_footer': True,
                'show_in_sidebar': False,
            },
        ]
        
        for profile_data in social_profiles:
            SocialMediaProfile.objects.update_or_create(
                platform=profile_data['platform'],
                defaults={
                    'profile_url': profile_data['profile_url'],
                    'display_text': profile_data['display_text'],
                    'icon_name': profile_data['icon_name'],
                    'order': profile_data['order'],
                    'is_active': profile_data.get('is_active', True),
                    'show_in_footer': profile_data['show_in_footer'],
                    'show_in_sidebar': profile_data['show_in_sidebar'],
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Created/updated social profile: {profile_data['platform']}"))
        
        # Create sample books (you'll replace these with Arun's actual books)
        books = [
            {
                'title': 'Reimagining India\'s Economy',
                'subtitle': 'The Caring Society',
                'description': 'A visionary examination of how India can build an economy centered on care, equity, and sustainability rather than conventional growth metrics.',
                'publisher': 'Penguin Random House India',
                'publication_year': 2024,
                'is_featured': True,
                'amazon_link': 'https://www.amazon.com/dp/XXXXXXX',
                'goodreads_link': 'https://www.goodreads.com/book/show/XXXXXXX',
            },
            {
                'title': 'A Leader\'s Guide to Shaping the Future',
                'subtitle': 'How to Thrive in an Age of Uncertainty',
                'description': 'Practical wisdom for leaders navigating complex systems and driving meaningful change in turbulent times.',
                'publisher': 'Berrett-Koehler Publishers',
                'publication_year': 2021,
                'is_featured': True,
                'amazon_link': 'https://www.amazon.com/dp/XXXXXXX',
                'goodreads_link': 'https://www.goodreads.com/book/show/XXXXXXX',
            },
            {
                'title': 'Transforming Systems',
                'subtitle': 'Why the World Needs a New Kind of Leadership',
                'description': 'Exploring how leaders can transform complex systems by understanding interconnectedness and fostering collaboration.',
                'publisher': 'Routledge',
                'publication_year': 2018,
                'is_featured': False,
                'amazon_link': 'https://www.amazon.com/dp/XXXXXXX',
                'goodreads_link': 'https://www.goodreads.com/book/show/XXXXXXX',
            },
            {
                'title': 'Learning to Dance in the Rain',
                'subtitle': 'The Mindset for Enduring Leadership',
                'description': 'Reflections on leadership resilience, adaptability, and finding purpose in challenging circumstances.',
                'publisher': 'Tata McGraw-Hill',
                'publication_year': 2015,
                'is_featured': False,
                'amazon_link': 'https://www.amazon.com/dp/XXXXXXX',
                'goodreads_link': 'https://www.goodreads.com/book/show/XXXXXXX',
            },
        ]
        
        for book_data in books:
            Book.objects.update_or_create(
                title=book_data['title'],
                defaults={
                    'subtitle': book_data['subtitle'],
                    'description': book_data['description'],
                    'publisher': book_data['publisher'],
                    'publication_year': book_data['publication_year'],
                    'is_featured': book_data['is_featured'],
                    'amazon_link': book_data['amazon_link'],
                    'goodreads_link': book_data['goodreads_link'],
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Created/updated book: {book_data['title']}"))
        
        # --- NEW SECTION: Import Articles from data.json ---
        import os
        import json
        from django.utils.text import slugify
        from datetime import datetime
        from gateway.models import Article  # Ensure 'Article' is in your imports at the top

        json_file_path = 'data.json' # Assuming it's in your project root

        if os.path.exists(json_file_path):
            self.stdout.write(self.style.MIGRATE_HEADING('\nImporting Articles from data.json...'))
            with open(json_file_path, 'r', encoding='utf-8') as file:
                article_data = json.load(file)

                for item in article_data:
                    # 1. Handle Themes for the article
                    theme_objs = []
                    for theme_name in item.get('themes', []):
                        # This links to the themes you created in the "buckets" section above
                        theme, created = Theme.objects.get_or_create(
                            name=theme_name,
                            defaults={'slug': slugify(theme_name), 'bucket': 'system'} 
                        )
                        theme_objs.append(theme)

                    # 2. Parse Date
                    raw_date = item.get('date', '2026-01-01')
                    published_date = datetime.strptime(raw_date, '%Y-%m-%d').date()

                    # 3. Create Article
                    article, created = Article.objects.update_or_create(
                        title=item.get('title'),
                        defaults={
                            'content': item.get('content'),
                            'type': item.get('type', 'READ'),
                            'published_date': published_date,
                            'video_url': item.get('video_url', ''),
                        }
                    )
                    article.themes.set(theme_objs)
                    
                    status = "Imported" if created else "Updated"
                    self.stdout.write(f"- {status}: {article.title}")
        else:
            self.stdout.write(self.style.WARNING(f'\nNote: {json_file_path} not found. Skipping article import.'))

        # --- END OF NEW SECTION ---

        self.stdout.write(self.style.SUCCESS('\n✅ Initial setup complete with Arun\'s structure!'))
        
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initial setup complete with Arun\'s structure!'))
        self.stdout.write(self.style.SUCCESS('\nKey features:'))
        self.stdout.write(self.style.SUCCESS('• Three thematic buckets as per Arun\'s organization'))
        self.stdout.write(self.style.SUCCESS('• LinkedIn marked as primary platform'))
        self.stdout.write(self.style.SUCCESS('• Twitter marked as inactive'))
        self.stdout.write(self.style.SUCCESS('• "Quiet Email List" for newsletter'))
        self.stdout.write(self.style.SUCCESS('\nNext steps:'))
        self.stdout.write(self.style.SUCCESS('1. Run migrations: python manage.py makemigrations && python manage.py migrate'))
        self.stdout.write(self.style.SUCCESS('2. Run this command again: python manage.py setup_initial_data'))
        self.stdout.write(self.style.SUCCESS('3. Visit /admin to review the structure'))
        self.stdout.write(self.style.SUCCESS('4. Test /themes/ page to see the three-bucket organization'))