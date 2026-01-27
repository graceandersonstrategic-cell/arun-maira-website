from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from .models import (
    Book, Theme, GatewayPage, SocialMediaProfile, ContactMessage, 
    NewsletterSubscriber, Article, Talk, UploadedFile, SiteSettings
)

# Custom Admin Configuration
admin.site.site_header = "Arun Maira Content Management"
admin.site.site_title = "Arun Maira Admin"
admin.site.index_title = "Welcome to Arun's Content Management Portal"

# ===== THEME ADMIN =====
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'bucket_display', 'order', 'article_count', 'external_link_display')
    list_filter = ('bucket',)
    search_fields = ('name', 'description')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'bucket', 'description')
        }),
        ('Navigation', {
            'fields': ('order', 'external_link')
        }),
    )
    
    def bucket_display(self, obj):
        """Display bucket with color coding matching reading.html"""
        colors = {
            'system': '#4a90e2',      # Blue - The System
            'me_us': '#2ecc71',       # Green - Me/Us
            'future_india': '#e74c3c' # Red - Future of India
        }
        color = colors.get(obj.bucket, '#95a5a6')
        
        # Get bucket display name matching reading.html
        bucket_mapping = {
            'system': 'The System',
            'me_us': 'Me/Us',
            'future_india': 'Future of India'
        }
        bucket_display = bucket_mapping.get(obj.bucket, obj.bucket.title())
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em; font-weight: bold;">{}</span>',
            color,
            bucket_display
        )
    bucket_display.short_description = 'Category'
    bucket_display.admin_order_field = 'bucket'
    
    def external_link_display(self, obj):
        if obj.external_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #8b7355; text-decoration: none;">'
                '<i class="fas fa-external-link-alt"></i> Reading Room</a>',
                obj.external_link
            )
        return mark_safe('<span style="color: #999;">—</span>')
    external_link_display.short_description = 'Reading Room'
    
    def article_count(self, obj):
        count = obj.article_set.count()
        return format_html(
            '<span style="background-color: #f3f4f6; color: #4b5563; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em;">{} article{}</span>',
            count,
            's' if count != 1 else ''
        )
    article_count.short_description = 'Articles'

# ===== GATEWAY PAGE ADMIN =====
@admin.register(GatewayPage)
class GatewayPageAdmin(admin.ModelAdmin):
    list_display = ('page_type_icon', 'title', 'nav_status_badge', 
                    'navigation_order', 'updated_at')
    list_editable = ('navigation_order',)
    search_fields = ('title', 'content')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Page Identification', {
            'fields': ('page_type', 'title')
        }),
        ('Content', {
            'fields': ('content', 'sidebar_content', 'featured_image')
        }),
        ('Navigation', {
            'fields': ('show_in_navigation', 'navigation_order')
        }),
        ('Metadata', {
            'fields': ('updated_at',)
        }),
    )
    
    def page_type_icon(self, obj):
        icons = {
            'home': '🏠',
            'about': '👤',
            'books': '📚',
            'themes': '🗂️',
            'media': '📰',
            'contact': '✉️',
            'connect': '🔗',
            'reading': '📖',
            'listening': '🎧',
            'articles': '📄',
            'talks': '🎤',
        }
        icon = icons.get(obj.page_type, '📄')
        return f"{icon} {obj.get_page_type_display()}"
    page_type_icon.short_description = 'Page Type'
    
    def nav_status_badge(self, obj):
        if obj.show_in_navigation:
            return "🟢 Visible"
        return "🔴 Hidden"
    nav_status_badge.short_description = 'Navigation'

# ===== BOOK ADMIN =====
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_year', 'is_featured', 
                    'amazon_link_display', 'goodreads_link_display')
    list_filter = ('is_featured', 'publication_year')
    search_fields = ('title', 'subtitle', 'description', 'publisher')
    list_editable = ('is_featured',)
    
    fieldsets = (
        ('Book Details', {
            'fields': ('title', 'subtitle', 'description', 'cover_image')
        }),
        ('Publication Info', {
            'fields': ('publisher', 'publication_year')
        }),
        ('Links', {
            'fields': ('amazon_link', 'goodreads_link')
        }),
        ('Display Options', {
            'fields': ('is_featured',)
        }),
    )
    
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 60px; object-fit: cover; '
                'border: 1px solid #e5e7eb;" />',
                obj.cover_image.url
            )
        return format_html(
            '<div style="width: 40px; height: 60px; background: #f3f4f6; '
            'display: flex; align-items: center; justify-content: center; '
            'color: #9ca3af; border: 1px solid #e5e7eb;">📚</div>'
        )
    cover_preview.short_description = 'Cover'
    
    def amazon_link_display(self, obj):
        if obj.amazon_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #ff9900; text-decoration: none;">'
                '<i class="fab fa-amazon"></i> Amazon</a>',
                obj.amazon_link
            )
        return format_html('<span style="color: #999;">—</span>')
    amazon_link_display.short_description = 'Amazon'
    
    def goodreads_link_display(self, obj):
        if obj.goodreads_link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #553b08; text-decoration: none;">'
                '<i class="fab fa-goodreads"></i> Goodreads</a>',
                obj.goodreads_link
            )
        return format_html('<span style="color: #999;">—</span>')
    goodreads_link_display.short_description = 'Goodreads'

# ===== ARTICLE ADMIN - UPDATED FOR reading.html =====
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status_display', 'category_display', 'subtopic_display', 
                    'publish_date', 'reading_time_display', 'article_preview')
    list_filter = ('status', 'category', 'subtopic', 'publish_date')
    search_fields = ('title', 'content', 'excerpt', 'category', 'subtopic')
    filter_horizontal = ('themes',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'admin_preview_link', 'admin_article_url')
    date_hierarchy = 'publish_date'
    actions = ['mark_as_published', 'mark_as_draft', 'mark_as_featured']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'status', 'featured_article'),
            'description': 'Essential article information'
        }),
        ('Categorization', {
            'fields': ('category', 'subtopic', 'themes'),
            'description': 'Match these to reading.html categories and subtopics'
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image', 'document')
        }),
        ('Reading Experience', {
            'fields': ('reading_time', 'estimated_read_time')
        }),
        ('Publication', {
            'fields': ('publish_date', 'external_link', 'admin_preview_link', 'admin_article_url')
        }),
        ('SEO & Metadata', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        colors = {
            'draft': '#6b7280',      # Gray
            'published': '#10b981',   # Green
            'archived': '#ef4444',    # Red
        }
        
        status_text = dict(Article.STATUS_CHOICES).get(obj.status, obj.status.title())
        color = colors.get(obj.status, '#6b7280')
        
        # Add star for featured articles
        featured_star = ' ⭐' if obj.featured_article else ''
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em; font-weight: bold;">{}{}</span>',
            color,
            status_text,
            featured_star
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def category_display(self, obj):
        # Match reading.html categories
        categories = {
            'system': ('The System', '#4a90e2'),  # Blue
            'me_us': ('Me/Us', '#2ecc71'),        # Green
            'india': ('Future of India', '#e74c3c') # Red
        }
        
        display_name, color = categories.get(obj.category, (obj.category.title(), '#95a5a6'))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            display_name
        )
    category_display.short_description = 'Category'
    category_display.admin_order_field = 'category'
    
    def subtopic_display(self, obj):
        # Match reading.html subtopics
        subtopic_colors = {
            # The System subtopics
            'complex-systems': '#3498db',
            'democracy-policy': '#2980b9',
            'evolution-economics': '#1abc9c',
            'jobs-employment': '#16a085',
            'business-ethics': '#27ae60',
            # Me/Us subtopics
            'purpose-lives': '#f39c12',
            'listening-others': '#d35400',
            # Future of India subtopic
            'future-india': '#c0392b'
        }
        
        color = subtopic_colors.get(obj.subtopic, '#95a5a6')
        
        # Get subtopic display name
        subtopic_mapping = {
            'complex-systems': 'Complex Systems: Social Change',
            'democracy-policy': 'Democracy and Public Policy',
            'evolution-economics': 'Evolution of Economics',
            'jobs-employment': 'Jobs and Employment',
            'business-ethics': 'Business Ethics',
            'purpose-lives': 'Purpose of Our Lives',
            'listening-others': 'Listening to Others',
            'future-india': 'Future of India'
        }
        
        display_name = subtopic_mapping.get(obj.subtopic, obj.subtopic.replace('-', ' ').title())
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em;">{}</span>',
            color,
            display_name
        )
    subtopic_display.short_description = 'Subtopic'
    
    def reading_time_display(self, obj):
        if obj.reading_time:
            return format_html(
                '<span style="background-color: #f3f4f6; color: #4b5563; padding: 2px 8px; '
                'border-radius: 12px; font-size: 0.85em; display: inline-flex; '
                'align-items: center; gap: 4px;">'
                '<i class="fas fa-clock" style="font-size: 0.8em;"></i> {} min</span>',
                obj.reading_time
            )
        return format_html('<span style="color: #999; font-style: italic;">—</span>')
    reading_time_display.short_description = 'Time'
    
    def article_preview(self, obj):
        """Show article title with excerpt preview"""
        excerpt = obj.excerpt[:100] + '...' if obj.excerpt and len(obj.excerpt) > 100 else obj.excerpt
        
        return format_html(
            '<div style="max-width: 300px;">'
            '<strong style="display: block; margin-bottom: 4px; color: #333;">{}</strong>'
            '<small style="color: #666; line-height: 1.3;">{}</small>'
            '</div>',
            obj.title[:50] + '...' if len(obj.title) > 50 else obj.title,
            excerpt or 'No excerpt'
        )
    article_preview.short_description = 'Article Preview'
    
    def admin_preview_link(self, obj):
        """Generate a preview link that matches reading.html structure"""
        if not obj.pk or not obj.slug:
            return 'Save article first to generate preview'
        
        try:
            # Generate URL based on reading.html structure
            if obj.subtopic:
                # For subtopic articles - matches reading.html#subtopic-slug format
                url = f"/reading.html#{obj.subtopic}/{obj.slug}"
                display_url = f"reading.html#{obj.subtopic}/{obj.slug}"
            else:
                # For general articles
                url = f"/reading.html#article/{obj.slug}"
                display_url = f"reading.html#article/{obj.slug}"
            
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<a href="{}" target="_blank" style="color: #8b7355; text-decoration: none; '
                'background: #f5f5f5; padding: 8px 12px; border-radius: 4px; display: inline-flex; '
                'align-items: center; gap: 6px;">'
                '<i class="fas fa-external-link-alt"></i> Preview in reading.html</a>'
                '</div>'
                '<small style="color: #666; font-family: monospace; background: #f9f9f9; '
                'padding: 4px 8px; border-radius: 3px; display: block; margin-top: 5px;">'
                '{}'
                '</small>',
                url,
                display_url
            )
        except Exception as e:
            return format_html(
                '<span style="color: #999; font-style: italic;">Error generating preview: {}</span>',
                str(e)
            )
    admin_preview_link.short_description = 'Preview Link'
    
    def admin_article_url(self, obj):
        """Show the URL structure for this article"""
        if obj.pk and obj.slug:
            if obj.subtopic:
                return format_html(
                    '<code style="background: #f8f9fa; padding: 4px 8px; border-radius: 3px; '
                    'font-family: monospace; font-size: 0.9em;">'
                    'reading.html#{}/{}</code>',
                    obj.subtopic,
                    obj.slug
                )
            return format_html(
                '<code style="background: #f8f9fa; padding: 4px 8px; border-radius: 3px; '
                'font-family: monospace; font-size: 0.9em;">'
                'reading.html#article/{}</code>',
                obj.slug
            )
        return '—'
    admin_article_url.short_description = 'Article URL'
    
    @admin.action(description="📢 Mark selected articles as published")
    def mark_as_published(self, request, queryset):
        updated = queryset.update(status='published', publish_date=timezone.now())
        self.message_user(request, f'✅ {updated} article(s) published successfully.')
    
    @admin.action(description="✏️ Mark selected articles as draft")
    def mark_as_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'📝 {updated} article(s) moved to draft.')
    
    @admin.action(description="⭐ Mark selected articles as featured")
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(featured_article=True)
        self.message_user(request, f'⭐ {updated} article(s) marked as featured.')
    
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
            )
        }

# ===== TALK ADMIN =====
@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type_display', 'event_date', 'duration_display', 
                    'has_media_display', 'is_featured')
    list_filter = ('media_type', 'event_date', 'is_featured')
    search_fields = ('title', 'description', 'event_name')
    filter_horizontal = ('themes',)
    readonly_fields = ('created_at', 'media_preview', 'preview_link')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'media_type', 'is_featured')
        }),
        ('Media', {
            'fields': ('media_file', 'external_link', 'thumbnail', 'media_preview', 'duration')
        }),
        ('Event Details', {
            'fields': ('event_name', 'event_date', 'themes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'preview_link')
        }),
    )
    
    def media_type_display(self, obj):
        icons = {
            'audio': 'fas fa-microphone',
            'video': 'fas fa-video',
            'interview': 'fas fa-comments',
            'lecture': 'fas fa-chalkboard-teacher',
            'conversation': 'fas fa-users'
        }
        icon = icons.get(obj.media_type, 'fas fa-file')
        
        display_text = dict(Talk.MEDIA_TYPE_CHOICES).get(obj.media_type, obj.media_type.title())
        
        return format_html(
            '<i class="{}" style="margin-right: 5px;"></i>{}',
            icon,
            display_text
        )
    media_type_display.short_description = 'Type'
    
    def duration_display(self, obj):
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f'{hours}h {minutes}m'
            return f'{minutes}m'
        return format_html('<span style="color: #999;">—</span>')
    duration_display.short_description = 'Duration'
    
    def has_media_display(self, obj):
        if obj.media_file:
            return format_html(
                '<span style="color: #10b981;"><i class="fas fa-check-circle"></i> File</span>'
            )
        elif obj.external_link:
            return format_html(
                '<span style="color: #3b82f6;"><i class="fas fa-external-link-alt"></i> Link</span>'
            )
        return format_html('<span style="color: #ef4444;"><i class="fas fa-times-circle"></i> No Media</span>')
    has_media_display.short_description = 'Media'
    
    def media_preview(self, obj):
        if obj.external_link and ('youtube.com' in obj.external_link or 'youtu.be' in obj.external_link):
            # Extract video ID safely
            if 'v=' in obj.external_link:
                video_id = obj.external_link.split('v=')[-1].split('&')[0]
            elif 'youtu.be/' in obj.external_link:
                video_id = obj.external_link.split('youtu.be/')[-1].split('?')[0]
            else:
                return 'Cannot extract YouTube video ID'
                
            return format_html(
                '<iframe width="300" height="169" src="https://www.youtube.com/embed/{}" '
                'frameborder="0" allowfullscreen></iframe>',
                video_id
            )
        elif obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 169px; '
                'object-fit: cover; border: 1px solid #e5e7eb;" />',
                obj.thumbnail.url
            )
        return 'No preview available'
    media_preview.short_description = 'Preview'
    
    def preview_link(self, obj):
        if obj.pk and obj.slug:
            try:
                # Generate talk preview URL matching your site structure
                url = f"/listening.html#{obj.slug}"
                return format_html(
                    '<a href="{}" target="_blank" style="color: #8b7355; text-decoration: none;">'
                    '<i class="fas fa-eye"></i> Preview Talk</a>',
                    url
                )
            except Exception:
                return format_html(
                    '<a href="/talk/{}/" target="_blank" style="color: #8b7355; text-decoration: none;">'
                    '<i class="fas fa-eye"></i> Preview Talk</a>',
                    obj.slug
                )
        return 'Save talk first to generate preview link'
    preview_link.short_description = 'Preview'

# ===== SOCIAL MEDIA PROFILE ADMIN =====
@admin.register(SocialMediaProfile)
class SocialMediaProfileAdmin(admin.ModelAdmin):
    list_display = ('platform_display', 'display_text', 'is_active_status', 'order', 
                    'show_in_footer', 'show_in_sidebar', 'profile_url_link')
    list_filter = ('is_active', 'show_in_footer', 'show_in_sidebar', 'platform')
    list_editable = ('order', 'show_in_footer', 'show_in_sidebar')
    search_fields = ('platform', 'display_text', 'profile_url', 'description')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('platform', 'profile_url', 'display_text', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon_name', 'order', 'is_active')
        }),
        ('Location Settings', {
            'fields': ('show_in_footer', 'show_in_sidebar'),
            'description': 'Choose where this profile link appears on the website'
        }),
    )
    
    def platform_display(self, obj):
        icon_name = obj.get_icon_name()
        platform_name = obj.get_platform_display()
        return format_html(
            '<i class="fab fa-{}" style="margin-right: 8px; color: #8b7355;"></i>{}',
            icon_name,
            platform_name
        )
    platform_display.short_description = 'Platform'
    
    def is_active_status(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: #10b981;">✓ Active</span>')
        return mark_safe('<span style="color: #ef4444;">✗ Inactive</span>')
    is_active_status.short_description = 'Status'
    
    def profile_url_link(self, obj):
        if obj.profile_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #8b7355; text-decoration: none;">'
                '<i class="fas fa-external-link-alt"></i> Visit</a>',
                obj.profile_url
            )
        return mark_safe('<span style="color: #999;">—</span>')
    profile_url_link.short_description = 'Profile URL'

# ===== UPLOADED FILE ADMIN =====
@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file_type_display', 'title', 'uploaded_at', 'is_public_display', 
                    'file_size_display', 'file_link')
    list_filter = ('file_type', 'is_public', 'uploaded_at')
    search_fields = ('title', 'description')
    readonly_fields = ('uploaded_at', 'file_size_display', 'file_preview')
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('File Information', {
            'fields': ('title', 'description', 'file_type', 'is_public')
        }),
        ('File Upload', {
            'fields': ('file', 'file_preview')
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'file_size_display')
        }),
    )
    
    def file_type_display(self, obj):
        icon = obj.get_file_icon()
        display_text = dict(UploadedFile.FILE_TYPE_CHOICES).get(obj.file_type, obj.file_type.title())
        
        return format_html(
            '<i class="{}" style="margin-right: 8px; color: #8b7355;"></i>{}',
            icon,
            display_text
        )
    file_type_display.short_description = 'Type'
    
    def is_public_display(self, obj):
        if obj.is_public:
            return format_html(
                '<span style="color: #10b981;"><i class="fas fa-eye"></i> Public</span>'
            )
        return format_html(
            '<span style="color: #ef4444;"><i class="fas fa-eye-slash"></i> Private</span>'
        )
    is_public_display.short_description = 'Visibility'
    
    def file_size_display(self, obj):
        return format_html(
            '<span style="background-color: #f3f4f6; color: #4b5563; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em;">{}</span>',
            obj.file_size()
        )
    file_size_display.short_description = 'Size'
    
    def file_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="color: #8b7355; text-decoration: none;">'
                '<i class="fas fa-download"></i> Download</a>',
                obj.file.url
            )
        return format_html('<span style="color: #999;">—</span>')
    file_link.short_description = 'File'
    
    def file_preview(self, obj):
        if obj.file_type == 'image' and obj.file:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; '
                'object-fit: contain; border: 1px solid #e5e7eb;" />',
                obj.file.url
            )
        elif obj.file:
            return format_html(
                '<div style="padding: 20px; background: #f9fafb; border: 1px solid #e5e7eb; '
                'border-radius: 4px; text-align: center;">'
                '<i class="{}" style="font-size: 48px; color: #9ca3af;"></i><br>'
                '<span style="color: #6b7280;">{}</span></div>',
                obj.get_file_icon(),
                obj.file.name.split('/')[-1]
            )
        return 'No file uploaded'
    file_preview.short_description = 'Preview'

# ===== CONTACT MESSAGE ADMIN =====
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'category_display', 'organization', 
                    'submitted_at', 'is_read', 'is_archived', 'message_preview') 
    list_filter = ('is_read', 'is_archived', 'category', 'submitted_at')
    search_fields = ('name', 'email', 'organization', 'message', 'notes')
    readonly_fields = ('submitted_at', 'name', 'email', 'organization', 
                      'category', 'message', 'notes')
    list_editable = ('is_read', 'is_archived') 
    actions = ['mark_as_read', 'mark_as_unread', 'archive_messages', 'unarchive_messages']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'organization', 'category')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Management', {
            'fields': ('is_read', 'is_archived', 'response_sent', 'notes')
        }),
        ('Metadata', {
            'fields': ('submitted_at',)
        }),
    )
    
    def category_display(self, obj):
        colors = {
            'general': '#6b7280',
            'speaking': '#8b7355',
            'media': '#3b82f6',
            'academic': '#10b981',
            'editorial': '#f59e0b',
            'other': '#ef4444'
        }
        color = colors.get(obj.category, '#6b7280')
        
        category_mapping = {
            'general': 'General Inquiry',
            'speaking': 'Speaking Engagement',
            'media': 'Media Inquiry',
            'academic': 'Academic/Research',
            'editorial': 'Editorial Inquiry',
            'other': 'Other'
        }
        category_text = category_mapping.get(obj.category, obj.category.title())
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em; font-weight: bold;">{}</span>',
            color,
            category_text
        )
    category_display.short_description = 'Category'
    
    def message_preview(self, obj):
        truncated = Truncator(obj.message).chars(60)
        return format_html(
            '<span title="{}" style="cursor: help;">{}{}</span>',
            obj.message,
            truncated,
            '...' if len(obj.message) > 60 else ''
        )
    message_preview.short_description = 'Message'
    
    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    
    @admin.action(description="Mark selected messages as unread")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    
    @admin.action(description="Archive selected messages")
    def archive_messages(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} message(s) archived.')
    
    @admin.action(description="Unarchive selected messages")
    def unarchive_messages(self, request, queryset):
        updated = queryset.update(is_archived=False)
        self.message_user(request, f'{updated} message(s) unarchived.')

# ===== NEWSLETTER SUBSCRIBER ADMIN =====
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'subscription_type_display', 'subscribed_at', 
                    'is_active', 'is_confirmed', 'notes_preview')  
    list_filter = ('is_active', 'is_confirmed', 'subscription_type', 'subscribed_at')
    search_fields = ('email', 'name', 'organization', 'notes')
    readonly_fields = ('subscribed_at', 'last_sent', 'confirmation_token')
    list_editable = ('is_active',)
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name', 'organization')
        }),
        ('Subscription Details', {
            'fields': ('subscription_type', 'is_active', 'is_confirmed', 
                      'confirmation_token', 'notes')
        }),
        ('Metadata', {
            'fields': ('subscribed_at', 'last_sent')
        }),
    )
    
    def subscription_type_display(self, obj):
        colors = {
            'general': '#6b7280',
            'articles': '#8b7355',
            'events': '#3b82f6',
            'full': '#10b981'
        }
        color = colors.get(obj.subscription_type, '#6b7280')
        
        type_mapping = {
            'general': 'General Updates',
            'articles': 'New Articles Only',
            'events': 'Events & Talks Only',
            'full': 'All Updates'
        }
        type_text = type_mapping.get(obj.subscription_type, obj.subscription_type.title())
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em; font-weight: bold;">{}</span>',
            color,
            type_text
        )
    subscription_type_display.short_description = 'Subscription Type'
    
    def notes_preview(self, obj):
        if obj.notes:
            truncated = Truncator(obj.notes).chars(30)
            return format_html(
                '<span title="{}" style="cursor: help;">{}{}</span>',
                obj.notes,
                truncated,
                '...' if len(obj.notes) > 30 else ''
            )
        return format_html('<span style="color: #999;">—</span>')
    notes_preview.short_description = 'Notes'
    
    @admin.action(description="Activate selected subscribers")
    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriber(s) activated.')
    
    @admin.action(description="Deactivate selected subscribers")
    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriber(s) deactivated.')

# ===== SITE SETTINGS ADMIN =====
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'contact_email', 'site_status', 'updated_at')
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Site Information', {
            'fields': ('site_title', 'site_tagline')
        }),
        ('Contact Information', {
            'fields': ('admin_email', 'contact_email')
        }),
        ('Features', {
            'fields': ('enable_comments', 'maintenance_mode')
        }),
        ('Integration', {
            'fields': ('google_analytics_id',)
        }),
        ('Theme Configuration', {
            'fields': ('default_theme_bucket_order',)
        }),
        ('Metadata', {
            'fields': ('updated_at',)
        }),
    )
    
    def site_status(self, obj):
        if not obj:
            return format_html('<span style="color: #999;"><i class="fas fa-question-circle"></i> No Settings</span>')
        
        if obj.maintenance_mode:
            return format_html(
                '<span style="color: #ef4444; font-weight: 500;"><i class="fas fa-exclamation-triangle"></i> '
                'MAINTENANCE MODE</span>'
            )
        else:
            return format_html(
                '<span style="color: #10b981; font-weight: 500;"><i class="fas fa-check-circle"></i> Live</span>'
            )
    
    site_status.short_description = 'Site Status'
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    actions = ['toggle_maintenance_mode']
    
    def toggle_maintenance_mode(self, request, queryset):
        for settings in queryset:
            settings.maintenance_mode = not settings.maintenance_mode
            settings.save()
        
        self.message_user(
            request, 
            f"Toggled maintenance mode for {queryset.count()} settings"
        )
    
    toggle_maintenance_mode.short_description = "Toggle maintenance mode"