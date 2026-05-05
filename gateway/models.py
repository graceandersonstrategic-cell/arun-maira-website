from django.db import models
import re
import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import uuid  # Added for unique slugs
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

class Theme(models.Model):
    """Represents the thematic sections in Arun's reading room"""
    BUCKET_CHOICES = [
        ('system', 'The System'),
        ('me_us', 'Me/Us'),
        ('future_india', 'Future of India'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    bucket = models.CharField(max_length=50, choices=BUCKET_CHOICES, default='system')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['bucket', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_bucket_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
class Book(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True) 
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='books/', blank=True)
    amazon_link = models.URLField(blank=True, verbose_name="Amazon Link")
    themes = models.ManyToManyField(Theme, related_name='books', blank=True)
    goodreads_link = models.URLField(blank=True, verbose_name="Goodreads Link")
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField()
    is_featured = models.BooleanField(
        default=False, 
        help_text="Feature this book on the homepage"
    )
    
    class Meta:
        ordering = ['-publication_year']
        verbose_name = "Book"
        verbose_name_plural = "Books"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        # We will create this 'book_detail' view next
        return reverse('book_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            # Check for uniqueness
            while Book.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Clean Amazon links
        if self.amazon_link and '?' in self.amazon_link:
            self.amazon_link = self.amazon_link.split('?')[0]
        
        super().save(*args, **kwargs)

class Article(models.Model):
    """For Arun to upload his articles/essays and Videos"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('system', 'The System'),
        ('me_us', 'Me/Us'),
        ('india', 'Future of India'),
        ('READ', 'Read (Articles)'),
    ]
    
    SUBTOPIC_CHOICES = [
        ('complex-systems', 'Complex Systems: Social Change'),
        ('democracy-policy', 'Democracy and Public Policy'),
        ('evolution-economics', 'Evolution of Economics'),
        ('jobs-employment', 'Jobs and Employment'),
        ('business-ethics', 'Business Ethics'),
        ('purpose-lives', 'Purpose of Our Lives'),
        ('listening-others', 'Listening to Others'),
        ('future-india', 'Future of India'),
    ]
    
    title = models.CharField(max_length=600)
    # This is the critical field for the Error 153 fix
    video_id = models.CharField(max_length=20, blank=True, null=True, help_text="YouTube Video ID (e.g., GomzK5HohO4)")
    # slug = models.SlugField(unique=True, blank=True, help_text="URL-friendly version (auto-generated)")
    slug = models.SlugField(max_length=600, unique=True) # Increased

    excerpt = models.TextField(blank=True, help_text="Short summary for cards")
    content = models.TextField(help_text="Main article content (can use basic HTML)")
    # themes = models.ManyToManyField(Theme, related_name='articles', blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system')
    subtopic = models.CharField(max_length=50, choices=SUBTOPIC_CHOICES, blank=True)
    publish_date = models.DateField(null=True, blank=True) # Add this field
    themes = models.ManyToManyField(Theme, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured_article = models.BooleanField(default=False)
    # publish_date = models.DateTimeField(default=timezone.now)
    
    featured_image = models.ImageField(upload_to='articles/images/%Y/%m/', blank=True)
    document = models.FileField(upload_to='articles/documents/%Y/%m/', blank=True)
    
    reading_time = models.IntegerField(blank=True, null=True)
    estimated_read_time = models.CharField(max_length=50, blank=True)
    
    external_link = models.URLField(blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish_date', '-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if not self.reading_time and self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)
            self.estimated_read_time = f"{self.reading_time} min read"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # Simplified to match your project's URL patterns
        return reverse('article_detail', kwargs={'slug': self.slug})

    @property
    def first_image(self):
        if self.featured_image:
            return self.featured_image.url

        match = re.search(r'src="([^"]+)"', self.content or "")
        if match:
            url = match.group(1)
        
            # Only process local media paths
            if "/media/" in url:
                # 1. Get the directory and the filename the database wants
                # e.g., 'articles/images/2026/01/' and 'rsw_540_23.jpg'
                clean_path = url.split('/media/')[-1]
                directory = os.path.join(settings.MEDIA_ROOT, os.path.dirname(clean_path))
                target_file = os.path.basename(clean_path)
            
                # 2. If the directory doesn't exist, fallback to live site
                if not os.path.exists(directory):
                    return f"https://www.arunmaira.com{url}"
            
                # 3. Check for the exact file
                if os.path.exists(os.path.join(directory, target_file)):
                    return url
            
                # 4. FUZZY MATCH: Look for a file that STARTS with the target name
                # This fixes 'rsw_540_23.jpg' vs 'rsw_540_23_kZkpGC7.jpg'
                base_name = os.path.splitext(target_file)[0] # 'rsw_540_23'
                for actual_file in os.listdir(directory):
                    if actual_file.startswith(base_name):
                        # Return the path to the actual file found on disk
                        relative_path = os.path.join(os.path.dirname(clean_path), actual_file)
                        return f"{settings.MEDIA_URL}{relative_path.replace('\\', '/')}"
            
                # 5. Ultimate Fallback: Point to the original live website
                return f"https://www.arunmaira.com/media/articles/images/2026/01/{target_file}"
                
            return url
        return None
    
class Talk(models.Model):
    """For Arun to upload audio/video recordings"""
    TYPE_CHOICES = [
        ('audio', 'Audio Recording'),
        ('video', 'Video Recording'),
        ('interview', 'Interview'),
        ('lecture', 'Lecture'),
        ('conversation', 'Conversation'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
            #Changed to blank=True so it's no longer required in Admin
    description = models.TextField(blank=True, null=True)
    themes = models.ManyToManyField(Theme, related_name='talks', blank=True) 
    media_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    media_file = models.FileField(
        upload_to='talks/media/%Y/%m/', 
        blank=True,
        help_text="Audio/Video file (max 500MB)"
    )
    external_link = models.URLField(
        blank=True, 
        help_text="YouTube, Vimeo, or other external link"
    )
    # New field to store the ID directly
    video_id = models.CharField(max_length=50, blank=True, editable=False)
    
    thumbnail = models.ImageField(upload_to='talks/thumbnails/%Y/%m/', blank=True)
    themes = models.ManyToManyField('Theme', blank=True)
    event_name = models.CharField(max_length=200, blank=True)
    event_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True, help_text="HH:MM:SS format")
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-event_date', '-created_at']
        verbose_name = "Talk"
        verbose_name_plural = "Talks"

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"

    def save(self, *args, **kwargs):
        # 1. Automatic Slug Generation with Uniqueness Check
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Talk.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # 2. Automatic YouTube ID Extraction
        if self.external_link:
            pattern = r'(?:v=|\/|embed\/|youtu.be\/)([0-9A-Za-z_-]{11})'
            match = re.search(pattern, self.external_link)
            if match:
                self.video_id = match.group(1)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Generate URL for listening page anchor"""
        return f"/listening/# {self.slug}"

    def has_media(self):
        return bool(self.media_file or self.external_link)

class UploadedFile(models.Model):
    """Simple file upload for various purposes"""
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True,
                                   help_text="Show this file to website visitors")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"
    
    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"
    
    def get_file_icon(self):
        icons = {
            'image': 'fa-image',
            'document': 'fa-file-pdf',
            'audio': 'fa-file-audio',
            'video': 'fa-file-video',
            'presentation': 'fa-file-powerpoint',
            'other': 'fa-file',
        }
        return icons.get(self.file_type, 'fa-file')
    
    def file_size(self):
        if self.file:
            size_bytes = self.file.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        return "Unknown"

class GatewayPage(models.Model):
    """Static pages like Home, About, Media, Contact"""
    PAGE_CHOICES = [
        ('home', 'Home'),
        ('about', 'About Arun'),
        ('books', 'Books'),
        ('themes', 'Themes Overview'),
        ('media', 'Media & Press'),
        ('contact', 'Contact'),
        ('reading', 'Reading Ideas'),
        ('listening', 'Listening to Ideas'),
        ('articles', 'Articles'),
        ('talks', 'Talks & Recordings'),
    ]
    
    page_type = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, 
        help_text="Main content (can use basic HTML)")
    sidebar_content = models.TextField(blank=True,
        help_text="Optional sidebar content")
    featured_image = models.ImageField(upload_to='pages/%Y/%m/', blank=True,
                                      help_text="Featured image for this page")
    updated_at = models.DateTimeField(auto_now=True)
    show_in_navigation = models.BooleanField(default=True,
                                            help_text="Show this page in main navigation")
    navigation_order = models.IntegerField(default=0,
                                          help_text="Order in navigation (lower numbers first)")
    
    class Meta:
        ordering = ['navigation_order', 'page_type']
        verbose_name = "Gateway Page"
        verbose_name_plural = "Gateway Pages"
    
    def __str__(self):
        return f"{self.get_page_type_display()} Page"
    
    def get_absolute_url(self):
        # Map page_type to URL patterns for reading.html and listening.html
        simple_url_map = {
            'home': '/',
            'about': '/about.html',
            'books': '/books.html',
            'themes': '/reading.html',  # Direct to reading.html
            'media': '/media.html',
            'contact': '/contact.html',
            'reading': '/reading.html',  # Direct link
            'listening': '/listening.html',    # Direct link
            'articles': '/reading.html#articles',
            'talks': '/listening.html#talks',
        }
        return simple_url_map.get(self.page_type, '/')

class SocialMediaProfile(models.Model):
    """Model for managing social media profiles with icon support"""
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('goodreads', 'Goodreads'),
        ('amazon', 'Amazon Author'),
        ('newsletter', 'Newsletter'),
    ]
    
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    profile_url = models.URLField()
    display_text = models.CharField(max_length=100, blank=True)
    icon_name = models.CharField(max_length=50, blank=True, 
        help_text="Font Awesome icon name (e.g., 'linkedin', 'envelope')")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    show_in_footer = models.BooleanField(default=True, 
        help_text="Show in website footer")
    show_in_sidebar = models.BooleanField(default=False, 
        help_text="Show in website sidebar")
    description = models.TextField(blank=True,
                                  help_text="Brief description of how Arun uses this platform")
    
    class Meta:
        ordering = ['order', 'platform']
        verbose_name = "Social Media Profile"
        verbose_name_plural = "Social Media Profiles"
    
    def __str__(self):
        return f"{self.get_platform_display()}"
    
    def get_display_text(self):
        return self.display_text or self.get_platform_display()
    
    def get_icon_name(self):
        """Return appropriate icon name based on platform if not specified"""
        if self.icon_name:
            return self.icon_name
        
        # Default icons for each platform
        icon_map = {
            'linkedin': 'linkedin',
            'twitter': 'twitter',
            'goodreads': 'goodreads',
            'amazon': 'amazon',
            'newsletter': 'envelope',
        }
        return icon_map.get(self.platform, 'link')

class ContactMessage(models.Model):
    """For contact form submissions"""
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('speaking', 'Speaking Engagement'),
        ('media', 'Media Inquiry'),
        ('academic', 'Academic/Research'),
        ('editorial', 'Editorial Inquiry'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    organization = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    response_sent = models.BooleanField(default=False,
                                       help_text="Response has been sent")
    notes = models.TextField(blank=True,
                            help_text="Internal notes about this inquiry")
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        indexes = [
            models.Index(fields=['is_read', 'submitted_at']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"Message from {self.name} ({self.get_category_display()})"
    
    def short_message(self):
        """Return truncated message for admin display"""
        if len(self.message) > 100:
            return self.message[:100] + "..."
        return self.message

class NewsletterSubscriber(models.Model):
    """Newsletter subscription management"""
    SUBSCRIPTION_TYPES = [
        ('general', 'General Updates'),
        ('articles', 'New Articles Only'),
        ('events', 'Events & Talks Only'),
        ('full', 'All Updates'),
    ]
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    subscription_type = models.CharField(max_length=50, choices=SUBSCRIPTION_TYPES, 
                                        default='general')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    notes = models.TextField(blank=True, 
        help_text="Optional notes about how they found the newsletter")
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(blank=True, null=True,
                                    help_text="Last newsletter sent to this subscriber")
    confirmation_token = models.CharField(max_length=100, blank=True)
    is_confirmed = models.BooleanField(default=False,
                                      help_text="Email address has been confirmed")
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['is_active', 'subscription_type']),
        ]
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.email} ({status})"
    
    def clean(self):
        """Validate email format"""
        from django.core.exceptions import ValidationError
        from django.core.validators import validate_email
        
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': 'Please enter a valid email address'})

class SiteSettings(models.Model):
    """Site-wide settings and configuration"""
    site_title = models.CharField(max_length=200, default="Arun Maira")
    site_tagline = models.CharField(max_length=300, blank=True, 
                                   default="A quiet space for thoughtful inquiry")
    admin_email = models.EmailField(default="admin@arunmaira.com")
    contact_email = models.EmailField(default="contact@arunmaira.com")
    site_status = models.BooleanField(
        default=True,
        verbose_name="Site Status",
        help_text="Overall site status (different from maintenance mode)"
    )
    
    google_analytics_id = models.CharField(max_length=50, blank=True)
    enable_comments = models.BooleanField(default=False,
                                         help_text="Enable comments on articles")
    maintenance_mode = models.BooleanField(default=False,
                                          help_text="Put site in maintenance mode")
    default_theme_bucket_order = models.CharField(max_length=200, default="system,me_us,future_india",
                                                 help_text="Order of theme buckets (comma-separated)")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one SiteSettings instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """Load or create site settings"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

# Signal imports
@receiver(pre_save, sender=Article)
def article_pre_save(sender, instance, **kwargs):
    """Auto-generate slug and reading time for articles"""
    if not instance.slug:
        instance.slug = slugify(instance.title)
    
    # Auto-calculate reading time if not provided
    if not instance.reading_time and instance.content:
        word_count = len(instance.content.split())
        instance.reading_time = max(1, word_count // 200)
        instance.estimated_read_time = f"{instance.reading_time} min read"
    elif instance.reading_time and not instance.estimated_read_time:
        instance.estimated_read_time = f"{instance.reading_time} min read"

@receiver(pre_save, sender=Talk)
def talk_pre_save(sender, instance, **kwargs):
    """Auto-generate slug for talks"""
    if not instance.slug:
        instance.slug = slugify(instance.title)

@receiver(pre_save, sender=Theme)
def theme_pre_save(sender, instance, **kwargs):
    """Auto-generate slug for themes"""
    if not instance.slug:
        instance.slug = slugify(instance.name)

@receiver(post_save, sender=SiteSettings)
def clear_cache(sender, instance, **kwargs):
    """Clear cache when site settings are updated"""
    from django.core.cache import cache
    cache.clear()