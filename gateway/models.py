from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
import uuid  # Added for unique slugs

class Book(models.Model):
    """Model for Arun's published books"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='books/', blank=True)
    amazon_link = models.URLField(blank=True, verbose_name="Amazon Link")
    goodreads_link = models.URLField(blank=True, verbose_name="Goodreads Link")
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField()
    is_featured = models.BooleanField(default=False, 
        help_text="Feature this book on the homepage")
    
    class Meta:
        ordering = ['-publication_year']
        verbose_name = "Book"
        verbose_name_plural = "Books"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('book_list')
    
    def save(self, *args, **kwargs):
        # Clean up URLs if needed
        if self.amazon_link and 'ref=dp_byline_sr_book' in self.amazon_link:
            # Extract clean Amazon author page URL
            self.amazon_link = "https://www.amazon.com/author/arunmaira"
        super().save(*args, **kwargs)

class Theme(models.Model):
    """Represents the thematic sections in Arun's reading room"""
    BUCKET_CHOICES = [
        ('system', 'The System'),
        ('me_us', 'Me/Us'),
        ('future_india', 'Future of India'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the name")
    description = models.TextField(blank=True)
    bucket = models.CharField(max_length=50, choices=BUCKET_CHOICES, 
                            default='system',
                            help_text="Which of Arun's three buckets this theme belongs to")
    external_link = models.URLField(blank=True, 
        help_text="Link to this theme in the existing reading room")
    order = models.IntegerField(default=0, help_text="Order in navigation")
    
    class Meta:
        ordering = ['bucket', 'order', 'name']
        verbose_name = "Theme"
        verbose_name_plural = "Themes"
    
    def __str__(self):
        return f"{self.name} ({self.get_bucket_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Article(models.Model):
    """For Arun to upload his articles/essays - Updated for reading.html integration"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    CATEGORY_CHOICES = [
        ('system', 'The System'),
        ('me_us', 'Me/Us'),
        ('india', 'Future of India'),
    ]
    
    SUBTOPIC_CHOICES = [
        # The System subtopics (matching reading.html)
        ('complex-systems', 'Complex Systems: Social Change'),
        ('democracy-policy', 'Democracy and Public Policy'),
        ('evolution-economics', 'Evolution of Economics'),
        ('jobs-employment', 'Jobs and Employment'),
        ('business-ethics', 'Business Ethics'),
        # Me/Us subtopics
        ('purpose-lives', 'Purpose of Our Lives'),
        ('listening-others', 'Listening to Others'),
        # Future of India subtopic
        ('future-india', 'Future of India'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, 
                           help_text="URL-friendly version (auto-generated)")
    excerpt = models.TextField(blank=True, help_text="Short summary for cards in reading.html")
    content = models.TextField(help_text="Main article content (can use basic HTML)")
    
    # Categorization (matching reading.html structure)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, 
                               default='system',
                               help_text="Main category matching reading.html")
    subtopic = models.CharField(max_length=50, choices=SUBTOPIC_CHOICES, blank=True,
                               help_text="Specific subtopic from reading.html")
    themes = models.ManyToManyField(Theme, blank=True, 
                                   help_text="Select relevant themes")
    
    # Status & Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured_article = models.BooleanField(default=False, 
                                          help_text="Feature this article (shows star in admin)")
    publish_date = models.DateTimeField(default=timezone.now, 
                                       help_text="When to publish")
    
    # Media & Files
    featured_image = models.ImageField(upload_to='articles/images/%Y/%m/', blank=True,
                                      help_text="Featured image for the article")
    document = models.FileField(upload_to='articles/documents/%Y/%m/', blank=True,
                               help_text="PDF or document file (optional)")
    
    # Reading Experience
    reading_time = models.IntegerField(blank=True, null=True, 
                                      help_text="Estimated reading time in minutes (auto-calculated)")
    estimated_read_time = models.CharField(max_length=50, blank=True,
                                          help_text="Auto-calculated: '5 min read'")
    
    # External Links
    external_link = models.URLField(blank=True, 
                                   help_text="Link if published elsewhere")
    
    # SEO & Metadata
    meta_description = models.TextField(blank=True, 
                                       help_text="SEO description (max 160 characters)")
    meta_keywords = models.CharField(max_length=200, blank=True,
                                    help_text="SEO keywords (comma-separated)")
    
    # System
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              help_text="Article author")
    
    class Meta:
        ordering = ['-publish_date', '-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        indexes = [
            models.Index(fields=['status', 'publish_date']),
            models.Index(fields=['category', 'subtopic']),
            models.Index(fields=['featured_article']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-calculate reading time if not provided
        if not self.reading_time and self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)  # 200 words per minute
            self.estimated_read_time = f"{self.reading_time} min read"
        elif self.reading_time and not self.estimated_read_time:
            self.estimated_read_time = f"{self.reading_time} min read"
        
        # Ensure publish_date is set for published articles
        if self.status == 'published' and not self.publish_date:
            self.publish_date = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Generate URL matching reading.html structure"""
        if self.subtopic:
            # Matches reading.html#subtopic-slug format
            return f"/reading.html#{self.subtopic}/{self.slug}"
        else:
            return f"/reading.html#article/{self.slug}"
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def display_category(self):
        """Get display name for category"""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    @property
    def display_subtopic(self):
        """Get display name for subtopic"""
        return dict(self.SUBTOPIC_CHOICES).get(self.subtopic, self.subtopic)
    
    def theme_names(self):
        return ", ".join([theme.name for theme in self.themes.all()])
    
    def get_preview_url(self):
        """Get preview URL for admin"""
        return self.get_absolute_url()
    
    def get_absolute_url(self):
        return reverse('reading_idea_detail', kwargs={'slug': self.slug})
    

class Talk(models.Model):
    """For Arun to upload audio/video recordings"""
    TYPE_CHOICES = [
        ('audio', 'Audio Recording'),
        ('video', 'Video Recording'),
        ('interview', 'Interview'),
        ('lecture', 'Lecture'),
        ('conversation', 'Conversation'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    media_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    media_file = models.FileField(upload_to='talks/media/%Y/%m/', blank=True,
                                 help_text="Audio/Video file (max 500MB)")
    external_link = models.URLField(blank=True, 
                                   help_text="YouTube, Vimeo, or other external link")
    thumbnail = models.ImageField(upload_to='talks/thumbnails/%Y/%m/', blank=True,
                                 help_text="Thumbnail image")
    themes = models.ManyToManyField(Theme, blank=True)
    event_name = models.CharField(max_length=200, blank=True)
    event_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True, 
                                   help_text="HH:MM:SS format")
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False, 
                                     help_text="Feature this talk on the listening page")
    
    class Meta:
        ordering = ['-event_date', '-created_at']
        verbose_name = "Talk"
        verbose_name_plural = "Talks"
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Generate URL for listening.html"""
        return f"/listening.html#{self.slug}"
    
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
        ('connect', 'Connect'),
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
            'connect': '/connect.html',
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
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('website', 'Website'),
        ('podcast', 'Podcast'),
        ('medium', 'Medium'),
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
            'youtube': 'youtube',
            'instagram': 'instagram',
            'facebook': 'facebook',
            'website': 'globe',
            'podcast': 'podcast',
            'medium': 'medium',
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
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

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