from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin

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

# ===== EXPORT RESOURCES =====
class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article
        fields = ('title', 'status', 'publish_date', 'reading_time')

class ContactMessageResource(resources.ModelResource):
    class Meta:
        model = ContactMessage

class NewsletterSubscriberResource(resources.ModelResource):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email', 'subscription_type', 'is_active', 'is_confirmed', 'subscribed_at')

# ===== THEME ADMIN =====
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'bucket_display', 'order', 'article_count')
    list_filter = ('bucket',)
    search_fields = ('name', 'description')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'bucket', 'description')
        }),
        ('Navigation', {
            'fields': ('order',)
        }),
    )
    
    def bucket_display(self, obj):
        colors = {
            'system': '#4a90e2',      
            'me_us': '#2ecc71',       
            'future_india': '#e74c3c' 
        }
        color = colors.get(obj.bucket, '#95a5a6')
        bucket_mapping = {
            'system': 'The System',
            'me_us': 'Me/Us',
            'future_india': 'Future of India'
        }
        bucket_display = bucket_mapping.get(obj.bucket, obj.bucket.title())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 0.85em; font-weight: bold;">{}</span>',
            color, bucket_display
        )
    bucket_display.short_description = 'Category'

    def article_count(self, obj):
        count = obj.article_set.count()
        return format_html('<span style="background-color: #f3f4f6; padding: 2px 8px; border-radius: 12px;">{}</span>', count)

# ===== GATEWAY PAGE ADMIN =====
@admin.register(GatewayPage)
class GatewayPageAdmin(admin.ModelAdmin):
    list_display = ('page_type_icon', 'title','show_in_navigation', 'nav_status_badge', 'navigation_order', 'updated_at')
    list_editable = ('navigation_order', 'show_in_navigation')
    search_fields = ('title', 'content')
    readonly_fields = ('updated_at',)
    
    def page_type_icon(self, obj):
        icons = {'home': '🏠', 'about': '👤', 'books': '📚', 'themes': '🗂️', 'media': '📰', 'contact': '✉️', 'reading': '📖', 'listening': '🎧'}
        return f"{icons.get(obj.page_type, '📄')} {obj.get_page_type_display()}"
    
    def nav_status_badge(self, obj):
        return "🟢 Visible" if obj.show_in_navigation else "🔴 Hidden"

# ===== BOOK ADMIN (UPDATED WITH PREVIEW & LIVE LINK) =====
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('cover_preview', 'title', 'publication_year', 'is_featured', 'amazon_link_display', 'view_on_site_link')
    list_filter = ('is_featured', 'publication_year')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('is_featured',)
    readonly_fields = ('view_on_site_link',)
    
    fieldsets = (
        ('Book Details', {'fields': ('title', 'subtitle', 'description', 'cover_image')}),
        ('Publication Info', {'fields': ('publisher', 'publication_year')}),
        ('Links', {'fields': ('amazon_link', 'goodreads_link')}),
        ('Display Options', {'fields': ('is_featured', 'view_on_site_link')}),
    )
    prepopulated_fields = {'slug': ('title',)}

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="width: 45px; height: 65px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />', obj.cover_image.url)
        return mark_safe('<div style="width: 45px; height: 65px; background: #eee; text-align: center; line-height: 65px;">📚</div>')
    cover_preview.short_description = 'Cover'

    def view_on_site_link(self, obj):
        if obj.pk:
            url = reverse('book_list')
            return format_html('<a href="{}" target="_blank" class="button" style="background: #8b7355; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">View in Library</a>', url)
        return "Save to preview"

    def amazon_link_display(self, obj):
        if obj.amazon_link:
            return format_html('<a href="{}" target="_blank" style="color: #ff9900;"><i class="fab fa-amazon"></i> Shop</a>', obj.amazon_link)
        return "—"

# ===== EXPORT RESOURCES =====
class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article
        fields = ('title', 'status', 'publish_date', 'reading_time')

class ContactMessageResource(resources.ModelResource):
    class Meta:
        model = ContactMessage

class NewsletterSubscriberResource(resources.ModelResource):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email', 'subscription_type', 'is_active', 'is_confirmed', 'subscribed_at')

# ===== ARTICLE ADMIN =====
@admin.register(Article)
class ArticleAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ArticleResource
    list_display = ('title', 'status_display', 'category_display', 'publish_date', 'article_preview')
    list_filter = ('status', 'category', 'publish_date')
    filter_horizontal = ('themes',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'admin_preview_link')
    
    def status_display(self, obj):
        color = '#10b981' if obj.status == 'published' else '#6b7280'
        return format_html('<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px;">{}</span>', color, obj.status.upper())

    def category_display(self, obj):
        return format_html('<span style="border: 1px solid #ddd; padding: 2px 8px; border-radius: 12px;">{}</span>', obj.get_category_display())

    def article_preview(self, obj):
        return format_html('<small style="color: #666;">{}</small>', Truncator(obj.excerpt or obj.content).chars(50))

    def admin_preview_link(self, obj):
        url = f"/reading.html#article/{obj.slug}"
        return format_html('<a href="{}" target="_blank">View on Website</a>', url)

# ===== TALK ADMIN =====
@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'event_date', 'has_media_display', 'is_featured')
    list_filter = ('media_type', 'is_featured')
    readonly_fields = ('media_preview',)
    filter_horizontal = ('themes',)
    prepopulated_fields = {'slug': ('title',)}

    def has_media_display(self, obj):
        icon = "✅" if obj.external_link or obj.media_file else "❌"
        return icon

    def media_preview(self, obj):
        if obj.youtube_id:
            return format_html(
                '<iframe width="320" height="180" src="https://www.youtube.com/embed/{}" frameborder="0"></iframe>', 
                obj.youtube_id
            )
        return "No Preview"
    
# ===== REMAINING UTILITY ADMINS =====
@admin.register(SocialMediaProfile)
class SocialMediaProfileAdmin(admin.ModelAdmin):
    list_display = ('platform', 'display_text', 'is_active', 'order')
    list_editable = ('order', 'is_active')

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ContactMessageResource
    list_display = ('name', 'email', 'submitted_at', 'is_read')
    list_editable = ('is_read',)
    readonly_fields = ('submitted_at', 'name', 'email', 'message')

@admin.register(NewsletterSubscriber)
class NewsletterAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = NewsletterSubscriberResource
    list_display = ('email', 'subscription_type', 'is_active', 'is_confirmed', 'subscribed_at')
    list_filter = ('is_active', 'subscription_type', 'is_confirmed')
    search_fields = ('email', 'name', 'organization')
    readonly_fields = ('subscribed_at', 'submitted_at')

# ===== SITE SETTINGS ADMIN =====
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'contact_email', 'maintenance_mode', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class NewsletterSubscriberResource(resources.ModelResource):
    class Meta:
        model = NewsletterSubscriber
        fields = ('email', 'subscription_type', 'is_active', 'is_confirmed', 'subscribed_at')

class ContactMessageResource(resources.ModelResource):
    class Meta:
        model = ContactMessage

class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article
        fields = ('title', 'status', 'publish_date', 'reading_time')
