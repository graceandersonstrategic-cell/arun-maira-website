from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django import forms
from django.views.decorators.http import require_GET
from django.utils import timezone
import os
from .forms import BookUploadForm
from .models import Book, Theme, GatewayPage, SocialMediaProfile, ContactMessage, NewsletterSubscriber, Article, Talk
from django.views.decorators.http import require_GET

from .models import (
    Book, Theme, GatewayPage, SocialMediaProfile, 
    ContactMessage, NewsletterSubscriber, Article, 
    Talk, UploadedFile, SiteSettings
)
from .forms import BookUploadForm, ArticleForm, TalkForm


@require_GET
def health_check(request):
    """Health check endpoint for Render/Railway monitoring"""
    return HttpResponse("OK", status=200)

# ========== SIMPLE FORMS FOR UPLOADING ==========
class ReadingUploadForm(forms.Form):
    """Form for uploading reading materials"""
    TYPES = [
        ('essay', 'Essay/Article'),
        ('book_excerpt', 'Book Excerpt'),
        ('research_paper', 'Research Paper'),
        ('thought', 'Thought/Reflection'),
        ('other', 'Other'),
    ]
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Title of the reading material'
        })
    )
    
    content_type = forms.ChoiceField(
        choices=TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    themes = forms.ModelMultipleChoiceField(
        queryset=Theme.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste your reading material here...'
        }),
        help_text="You can use basic HTML tags for formatting"
    )
    
    external_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/article (if published elsewhere)'
        })
    )
    
    document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }),
        help_text="Upload PDF, DOC, or TXT file (optional)"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes or context...'
        })
    )
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # Validate file extension
            valid_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
            ext = os.path.splitext(document.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Unsupported file type. Allowed: {", ".join(valid_extensions)}'
                )
            
            # Validate file size (10MB limit)
            if document.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File too large ( > 10MB )")
        
        return document

class ListeningUploadForm(forms.Form):
    """Form for uploading listening materials"""
    TYPES = [
        ('audio', 'Audio Recording'),
        ('video', 'Video Recording'),
        ('podcast', 'Podcast Episode'),
        ('interview', 'Interview'),
        ('lecture', 'Lecture/Talk'),
        ('conversation', 'Conversation/Dialogue'),
        ('other', 'Other'),
    ]
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Title of the talk/recording'
        })
    )
    
    content_type = forms.ChoiceField(
        choices=TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    themes = forms.ModelMultipleChoiceField(
        queryset=Theme.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Description of the recording...'
        })
    )
    
    external_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'YouTube, Vimeo, or other external link'
        })
    )
    
    media_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }),
        help_text="Upload audio/video file (MP3, MP4, WAV, etc.)"
    )
    
    event_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Event/conference name (optional)'
        })
    )
    
    event_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    duration = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'HH:MM:SS or MM:SS (optional)'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes...'
        })
    )
    
    def clean_media_file(self):
        media_file = self.cleaned_data.get('media_file')
        if media_file:
            # Validate file extension
            valid_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.avi', '.mov', '.mkv']
            ext = os.path.splitext(media_file.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Unsupported file type. Allowed: {", ".join(valid_extensions)}'
                )
            
            # Validate file size (500MB limit)
            if media_file.size > 500 * 1024 * 1024:
                raise forms.ValidationError("File too large ( > 500MB )")
        
        return media_file

# ========== PUBLIC VIEWS ==========

def home(request):
    """Home page view"""
    try:
        page = GatewayPage.objects.get(page_type='home')
    except GatewayPage.DoesNotExist:
        page = None
    
    featured_books = Book.objects.filter(is_featured=True)[:3]
    all_themes = Theme.objects.all()[:6]
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    # Get recent articles for homepage
    recent_articles = Article.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:3]
    
    return render(request, 'home.html', {
        'page': page,
        'featured_books': featured_books,
        'themes': all_themes,
        'social_media_profiles': social_profiles,
        'recent_articles': recent_articles,
    })

def about(request):
    """About page view"""
    try:
        page = GatewayPage.objects.get(page_type='about')
    except GatewayPage.DoesNotExist:
        page = None
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'about.html', {
        'page': page,
        'social_media_profiles': social_profiles,
    })

def book_list(request):
    """Books page view"""
    try:
        page = GatewayPage.objects.get(page_type='books')
    except GatewayPage.DoesNotExist:
        page = None
    
    books = Book.objects.all().order_by('-publication_year')
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'books.html', {
        'page': page,
        'books': books,
        'social_media_profiles': social_profiles,
    })

def book_detail(request, book_id):
    """Individual book page"""
    book = get_object_or_404(Book, id=book_id)
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'book_detail.html', {
        'book': book,
        'social_media_profiles': social_profiles,
    })

def theme_list(request):
    """Themes overview page"""
    try:
        page = GatewayPage.objects.get(page_type='themes')
    except GatewayPage.DoesNotExist:
        page = None
    
    themes = Theme.objects.all()
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'themes.html', {
        'page': page,
        'themes': themes,
        'social_media_profiles': social_profiles,
    })

def theme_detail(request, slug):
    """Individual theme page with related content"""
    theme = get_object_or_404(Theme, slug=slug)
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    # Get related articles and books
    related_articles = Article.objects.filter(
        themes=theme, 
        status='published',
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:5]
    
    related_books = Book.objects.all()[:3]
    
    return render(request, 'theme_detail.html', {
        'theme': theme,
        'related_articles': related_articles,
        'related_books': related_books,
        'social_media_profiles': social_profiles,
    })

def media(request):
    """Media and press page"""
    try:
        page = GatewayPage.objects.get(page_type='media')
    except GatewayPage.DoesNotExist:
        page = None
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'media.html', {
        'page': page,
        'social_media_profiles': social_profiles,
    })

@csrf_exempt
def contact(request):
    """Contact page with form submission"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Handle AJAX form submission
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        organization = request.POST.get('organization', '').strip()
        purpose = request.POST.get('purpose', '').strip()
        message_content = request.POST.get('message', '').strip()
        
        # Basic validation
        if not name or not email or not message_content:
            return JsonResponse({'success': False, 'message': 'Please fill in all required fields.'})
        
        # Save to database
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            organization=organization,
            message=f"Purpose: {purpose}\n\n{message_content}"
        )
        
        # Optional: Send email notification
        try:
            send_mail(
                subject=f'New Contact Form Submission from {name}',
                message=f"""
                Name: {name}
                Email: {email}
                Organization: {organization}
                Purpose: {purpose}
                
                Message:
                {message_content}
                
                ---
                This message was sent from Arun Maira's website contact form.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@example.com'],
                fail_silently=True,
            )
        except:
            pass  # Don't break if email fails
        
        return JsonResponse({
            'success': True, 
            'message': 'Thank you for your message. Arun receives many inquiries and will respond only if the engagement aligns with his current priorities and availability.'
        })
    
    # GET request - render the contact page
    try:
        page = GatewayPage.objects.get(page_type='contact')
    except GatewayPage.DoesNotExist:
        page = None
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'contact.html', {
        'page': page,
        'social_media_profiles': social_profiles,
    })

def listening(request):
    """Listening to Ideas page"""
    # Get social media profiles for footer
    social_profiles = SocialMediaProfile.objects.filter(
        is_active=True, 
        show_in_footer=True
    ).order_by('order')
    
    # Get sidebar social profiles
    sidebar_profiles = SocialMediaProfile.objects.filter(
        is_active=True, 
        show_in_sidebar=True
    ).order_by('order')
    
    # Get talks/recordings
    talks = Talk.objects.all().order_by('-event_date', '-created_at')
    
    # Try to get page content from GatewayPage
    try:
        page = GatewayPage.objects.get(page_type='listening')
    except GatewayPage.DoesNotExist:
        page = None
    
    context = {
        'title': 'Listening',
        'author': 'Arun Maira',
        'page': page,
        'talks': talks,
        'social_media_profiles': social_profiles,
        'social_media_sidebar': sidebar_profiles,
    }
    
    return render(request, 'listening.html', context)

def talk_detail(request, slug):
    """Individual talk detail page"""
    talk = get_object_or_404(Talk, slug=slug)
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    sidebar_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_sidebar=True)
    
    # Get related talks
    related_talks = Talk.objects.filter(
        themes__in=talk.themes.all()
    ).exclude(id=talk.id).distinct()[:3]
    
    return render(request, 'talk_detail.html', {
        'talk': talk,
        'related_talks': related_talks,
        'social_media_profiles': social_profiles,
        'social_media_sidebar': sidebar_profiles,
    })

def reading(request):
    """Reading Ideas page - UPDATED FOR NEW TEMPLATE"""
    # Get all themes and group by bucket
    themes = Theme.objects.all().order_by('bucket', 'order', 'name')
    
    # Get published articles with current or past publish dates
    articles = Article.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).order_by('-publish_date', '-created_at')
    
    # DEBUG: Print to console
    print(f"\n=== DEBUG READING VIEW ===")
    print(f"Total articles in DB: {Article.objects.count()}")
    print(f"Published articles: {Article.objects.filter(status='published').count()}")
    print(f"Articles with past dates: {articles.count()}")
    
    for article in articles:
        print(f"  - {article.title} (Date: {article.publish_date}, Status: {article.status})")
    print("=== END DEBUG ===\n")
    
    # Get social media profiles for footer
    social_profiles = SocialMediaProfile.objects.filter(
        is_active=True, 
        show_in_footer=True
    ).order_by('order')
    
    # Get sidebar social profiles
    sidebar_profiles = SocialMediaProfile.objects.filter(
        is_active=True, 
        show_in_sidebar=True
    ).order_by('order')
    
    # Check if we have a GatewayPage for reading
    try:
        page = GatewayPage.objects.get(page_type='reading')
    except GatewayPage.DoesNotExist:
        page = None
    
    # Group themes by bucket for better display
    theme_buckets = {}
    for theme in themes:
        bucket = theme.get_bucket_display()
        if bucket not in theme_buckets:
            theme_buckets[bucket] = []
        theme_buckets[bucket].append(theme)
    
    # Debug output (remove in production)
    print(f"DEBUG: Found {articles.count()} articles")
    for article in articles:
        print(f"  - {article.title} (Status: {article.status}, Date: {article.publish_date})")
    
    context = {
        'theme_buckets': theme_buckets,
        'articles': articles,
        'page': page,
        'social_media_profiles': social_profiles,
        'social_media_sidebar': sidebar_profiles,
        'has_database_themes': themes.exists(),
    }
    
    return render(request, 'reading.html', context)

def reading_subtopic(request, subtopic=None):
    """
    Render reading.html with specific subtopic loaded
    """
    # Get social media profiles for footer
    social_profiles = SocialMediaProfile.objects.filter(
        is_active=True, 
        show_in_footer=True
    ).order_by('order')
    
    # Get sidebar social profiles
    sidebar_profiles = SocialMediaProfile.objects.filter(
        is_active=True, 
        show_in_sidebar=True
    ).order_by('order')
    
    # Check if we have a GatewayPage for reading
    try:
        page = GatewayPage.objects.get(page_type='reading')
    except GatewayPage.DoesNotExist:
        page = None
    
    # Get themes
    themes = Theme.objects.all().order_by('bucket', 'order', 'name')
    
    # Filter articles by subtopic if specified
    if subtopic:
        articles = Article.objects.filter(
            subtopic=subtopic,
            status='published',
            publish_date__lte=timezone.now()
        ).order_by('-publish_date', '-created_at')
        subtopic_display = dict(Article.SUBTOPIC_CHOICES).get(subtopic, subtopic.replace('-', ' ').title())
    else:
        articles = Article.objects.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).order_by('-publish_date', '-created_at')
        subtopic_display = 'All Topics'
    
    # Group themes by bucket for better display
    theme_buckets = {}
    for theme in themes:
        bucket = theme.get_bucket_display()
        if bucket not in theme_buckets:
            theme_buckets[bucket] = []
        theme_buckets[bucket].append(theme)
    
    context = {
        'subtopic': subtopic,
        'subtopic_display': subtopic_display,
        'page_title': subtopic_display,
        'meta_description': get_subtopic_description(subtopic),
        'theme_buckets': theme_buckets,
        'articles': articles,
        'page': page,
        'social_media_profiles': social_profiles,
        'social_media_sidebar': sidebar_profiles,
        'has_database_themes': themes.exists(),
    }
    return render(request, 'reading.html', context)

def reading_idea_detail(request, slug):
    """Individual reading idea detail page - same as article_detail"""
    # Get the article
    article = get_object_or_404(Article, slug=slug)
    
    # Check if article is published or user has permission
    if article.status != 'published':
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied("This article is not published yet.")
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    sidebar_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_sidebar=True)
    
    # Get related articles (same category or themes)
    related_articles = Article.objects.filter(
        Q(category=article.category) | Q(themes__in=article.themes.all()),
        status='published',
        publish_date__lte=timezone.now()
    ).exclude(id=article.id).distinct()[:3]
    
    # Get related books
    related_books = Book.objects.all()[:3]
    
    return render(request, 'reading_idea_detail.html', {
        'article': article,
        'related_articles': related_articles,
        'related_books': related_books,
        'social_media_profiles': social_profiles,
        'social_media_sidebar': sidebar_profiles,
    })

def article_detail(request, slug):
    """Individual article detail page - alias for reading_idea_detail"""
    return reading_idea_detail(request, slug)

def connect(request):
    """Connect page with social media links"""
    try:
        page = GatewayPage.objects.get(page_type='connect')
    except GatewayPage.DoesNotExist:
        page = None
    
    # Get all active social media profiles
    social_profiles = SocialMediaProfile.objects.filter(is_active=True).order_by('order')
    
    return render(request, 'connect.html', {
        'page': page,
        'social_media_profiles': social_profiles,
    })

@csrf_exempt
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        email = request.POST.get('email', '').strip()
        name = request.POST.get('name', '').strip()
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Please provide a valid email address.'})
        
        # Check if email is valid format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'message': 'Please provide a valid email address.'})
        
        # Save subscriber
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'is_active': True,
                'notes': 'Subscribed via website form'
            }
        )
        
        if created:
            message = 'Thank you. You have been added to the quiet list for occasional writings.'
        else:
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                message = 'Welcome back. Your subscription has been reactivated.'
            else:
                message = 'This email is already on the quiet list.'
        
        return JsonResponse({'success': True, 'message': message})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# ========== SUBTOPIC VIEWS FOR NAVIGATION ==========

def complex_systems(request):
    """Complex Systems: Social Change subtopic page"""
    return reading_subtopic(request, 'complex-systems')

def democracy_policy(request):
    """Democracy and Public Policy subtopic page"""
    return reading_subtopic(request, 'democracy-policy')

def evolution_economics(request):
    """Evolution of Economics subtopic page"""
    return reading_subtopic(request, 'evolution-economics')

def jobs_employment(request):
    """Jobs and Employment subtopic page"""
    return reading_subtopic(request, 'jobs-employment')

def business_ethics(request):
    """Business Ethics subtopic page"""
    return reading_subtopic(request, 'business-ethics')

def purpose_lives(request):
    """Purpose of Our Lives subtopic page"""
    return reading_subtopic(request, 'purpose-lives')

def listening_others(request):
    """Listening to Others subtopic page"""
    return reading_subtopic(request, 'listening-others')

def future_india(request):
    """Future of India subtopic page"""
    return reading_subtopic(request, 'future-india')

# ========== AUTHOR DASHBOARD VIEWS ==========

@login_required
def author_dashboard(request):
    """Author dashboard page - requires login"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    # Get counts for dashboard
    book_count = Book.objects.count()
    article_count = Article.objects.filter(status='published').count()
    talk_count = Talk.objects.count()
    contact_count = ContactMessage.objects.filter(is_read=False).count()
    subscriber_count = NewsletterSubscriber.objects.filter(is_active=True).count()
    
    # Recent content
    recent_books = Book.objects.order_by('-id')[:3]
    recent_articles = Article.objects.order_by('-created_at')[:3]
    recent_talks = Talk.objects.order_by('-created_at')[:3]
    recent_messages = ContactMessage.objects.filter(is_read=False).order_by('-submitted_at')[:5]
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/dashboard.html', {
        'book_count': book_count,
        'article_count': article_count,
        'talk_count': talk_count,
        'contact_count': contact_count,
        'subscriber_count': subscriber_count,
        'recent_books': recent_books,
        'recent_articles': recent_articles,
        'recent_talks': recent_talks,
        'recent_messages': recent_messages,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.add_book', raise_exception=True)
def upload_book(request):
    """View for authors to upload books"""
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" uploaded successfully!')
            return redirect('manage_books')
    else:
        form = BookUploadForm()
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/upload_book.html', {
        'form': form,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.change_book', raise_exception=True)
def edit_book(request, book_id):
    """Edit an existing book"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('manage_books')
    else:
        form = BookUploadForm(instance=book)
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/edit_book.html', {
        'form': form,
        'book': book,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.delete_book', raise_exception=True)
def delete_book(request, book_id):
    """Delete a book"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted successfully!')
        return redirect('manage_books')
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/delete_book.html', {
        'book': book,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.change_book', raise_exception=True)
def manage_books(request):
    """View for authors to manage their books"""
    books = Book.objects.all().order_by('-publication_year')
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/manage_books.html', {
        'books': books,
        'social_media_profiles': social_profiles,
    })

@login_required
def upload_reading(request):
    """Upload reading content - requires login"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ReadingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create an Article from the form data
            article_data = {
                'title': form.cleaned_data['title'],
                'content': form.cleaned_data['content'],
                'status': 'draft',  # Start as draft
                'external_link': form.cleaned_data.get('external_link', ''),
                'notes': form.cleaned_data.get('notes', ''),
            }
            
            # Create the article
            article = Article.objects.create(**article_data)
            
            # Add themes
            themes = form.cleaned_data.get('themes', [])
            if themes:
                article.themes.set(themes)
            
            # Handle document upload if provided
            if form.cleaned_data.get('document'):
                # Save document to UploadedFile model
                uploaded_file = UploadedFile.objects.create(
                    title=f"Document for: {article.title}",
                    description=f"Uploaded reading material: {form.cleaned_data['content_type']}",
                    file=form.cleaned_data['document'],
                    file_type='document',
                    is_public=True
                )
                article.document = uploaded_file.file
                article.save()
            
            messages.success(request, f'Reading material "{article.title}" uploaded successfully!')
            return redirect('reading')
    else:
        form = ReadingUploadForm()
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/upload_reading.html', {
        'form': form,
        'social_media_profiles': social_profiles,
    })

@login_required
def upload_listening(request):
    """Upload listening content - requires login"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = ListeningUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a Talk from the form data
            talk_data = {
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'media_type': form.cleaned_data['content_type'],
                'external_link': form.cleaned_data.get('external_link', ''),
                'event_name': form.cleaned_data.get('event_name', ''),
                'event_date': form.cleaned_data.get('event_date'),
            }
            
            # Parse duration if provided
            duration_str = form.cleaned_data.get('duration', '')
            if duration_str:
                try:
                    from datetime import timedelta
                    parts = duration_str.split(':')
                    if len(parts) == 3:
                        hours, minutes, seconds = map(int, parts)
                        talk_data['duration'] = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    elif len(parts) == 2:
                        minutes, seconds = map(int, parts)
                        talk_data['duration'] = timedelta(minutes=minutes, seconds=seconds)
                except ValueError:
                    pass  # Ignore duration if invalid
            
            # Create the talk
            talk = Talk.objects.create(**talk_data)
            
            # Add themes
            themes = form.cleaned_data.get('themes', [])
            if themes:
                talk.themes.set(themes)
            
            # Handle media file upload if provided
            if form.cleaned_data.get('media_file'):
                talk.media_file = form.cleaned_data['media_file']
                talk.save()
            
            messages.success(request, f'Listening material "{talk.title}" uploaded successfully!')
            return redirect('listening')
    else:
        form = ListeningUploadForm()
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/upload_listening.html', {
        'form': form,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.add_article', raise_exception=True)
def upload_article(request):
    """Upload article content - requires login"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Save many-to-many relationships (themes)
            messages.success(request, f'Article "{article.title}" uploaded successfully!')
            return redirect('manage_articles')
    else:
        form = ArticleForm()
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/upload_article.html', {
        'form': form,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.change_article', raise_exception=True)
def manage_articles(request):
    """Manage articles"""
    articles = Article.objects.all().order_by('-created_at')
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/manage_articles.html', {
        'articles': articles,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.add_talk', raise_exception=True)
def upload_talk(request):
    """Upload talk content - requires login"""
    if request.method == 'POST':
        form = TalkForm(request.POST, request.FILES)
        if form.is_valid():
            talk = form.save()
            messages.success(request, f'Talk "{talk.title}" uploaded successfully!')
            return redirect('manage_talks')
    else:
        form = TalkForm()
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/upload_talk.html', {
        'form': form,
        'social_media_profiles': social_profiles,
    })

@login_required
@permission_required('gateway.change_talk', raise_exception=True)
def manage_talks(request):
    """Manage talks"""
    talks = Talk.objects.all().order_by('-event_date', '-created_at')
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/manage_talks.html', {
        'talks': talks,
        'social_media_profiles': social_profiles,
    })

@login_required
def manage_contact_messages(request):
    """Manage contact messages"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    messages_list = ContactMessage.objects.all().order_by('-submitted_at')
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'author/manage_contact_messages.html', {
        'messages': messages_list,
        'unread_count': unread_count,
        'social_media_profiles': social_profiles,
    })

@login_required
def mark_message_read(request, message_id):
    """Mark a message as read"""
    if not request.user.is_staff:
        raise PermissionDenied
    
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    
    messages.success(request, 'Message marked as read.')
    return redirect('manage_contact_messages')

# Custom login view
def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('author_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully.')
                return redirect('author_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

@login_required
def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

# ========== HELPER FUNCTIONS ==========

def get_subtopic_display_name(subtopic):
    """Get display name for subtopic"""
    if subtopic:
        return dict(Article.SUBTOPIC_CHOICES).get(subtopic, subtopic.replace('-', ' ').title())
    return 'All Topics'

def get_subtopic_description(subtopic):
    """Get description for subtopic"""
    descriptions = {
        'complex-systems': 'Exploring how complex systems theory applies to social change and transformation.',
        'democracy-policy': 'Examining the relationship between democratic processes and effective policymaking.',
        'evolution-economics': 'Tracing the development of economic thought and exploring future directions.',
        'jobs-employment': 'Examining the future of work, employment trends, and meaningful livelihoods.',
        'business-ethics': 'Exploring ethical considerations in business practices and corporate responsibility.',
        'purpose-lives': 'Exploring meaning, purpose, and fulfillment in personal and professional life.',
        'listening-others': 'The art and practice of deep listening in personal and professional relationships.',
        'future-india': 'Contemplating India\'s path forward through multiple lenses and perspectives.',
    }
    return descriptions.get(subtopic, 'Articles and ideas from Arun Maira.')

def get_category_from_subtopic(subtopic):
    """Get category for a subtopic"""
    category_mapping = {
        'complex-systems': 'system',
        'democracy-policy': 'system',
        'evolution-economics': 'system',
        'jobs-employment': 'system',
        'business-ethics': 'system',
        'purpose-lives': 'me_us',
        'listening-others': 'me_us',
        'future-india': 'india',
    }
    return category_mapping.get(subtopic, 'system')

# ========== API VIEWS ==========

@require_GET
def article_list_api(request):
    """API endpoint to get all published articles"""
    articles = Article.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')
    
    data = []
    for article in articles:
        data.append({
            'id': article.slug,
            'title': article.title,
            'excerpt': article.excerpt,
            'date': article.publish_date.strftime('%b %d, %Y'),
            'readTime': article.estimated_read_time or f"{article.reading_time} min",
            'category': article.category,
            'subtopic': article.subtopic,
            'category_display': article.get_category_display(),
            'subtopic_display': article.get_subtopic_display(),
            'content': article.content,
            'featured_image': article.featured_image.url if article.featured_image else None,
        })
    
    return JsonResponse({'articles': data})

@require_GET
def articles_by_subtopic_api(request, subtopic):
    """API endpoint to get articles by subtopic"""
    articles = Article.objects.filter(
        status='published',
        subtopic=subtopic,
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')
    
    data = []
    for article in articles:
        data.append({
            'id': article.slug,
            'title': article.title,
            'excerpt': article.excerpt,
            'date': article.publish_date.strftime('%b %d, %Y'),
            'readTime': article.estimated_read_time or f"{article.reading_time} min",
            'category': article.category,
            'subtopic': article.subtopic,
            'category_display': article.get_category_display(),
            'subtopic_display': article.get_subtopic_display(),
            'content': article.content,
        })
    
    return JsonResponse({
        'subtopic': subtopic,
        'subtopic_display': get_subtopic_display_name(subtopic),
        'category': get_category_from_subtopic(subtopic),
        'articles': data
    })

@require_GET
def article_detail_api(request, slug):
    """API endpoint to get a specific article"""
    article = get_object_or_404(Article, slug=slug)
    
    # Check if article is published or user has permission
    if article.status != 'published':
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({'error': 'Article not found'}, status=404)
    
    data = {
        'id': article.slug,
        'title': article.title,
        'excerpt': article.excerpt,
        'date': article.publish_date.strftime('%b %d, %Y'),
        'readTime': article.estimated_read_time or f"{article.reading_time} min",
        'category': article.category,
        'subtopic': article.subtopic,
        'category_display': article.get_category_display(),
        'subtopic_display': article.get_subtopic_display(),
        'content': article.content,
        'featured_image': article.featured_image.url if article.featured_image else None,
        'document': article.document.url if article.document else None,
        'external_link': article.external_link,
        'themes': [theme.name for theme in article.themes.all()],
    }
    
    return JsonResponse(data)

@require_GET
def recent_articles_api(request):
    """API endpoint to get recent articles"""
    articles = Article.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')[:6]
    
    data = []
    for article in articles:
        data.append({
            'id': article.slug,
            'title': article.title,
            'excerpt': article.excerpt[:100] + '...' if len(article.excerpt) > 100 else article.excerpt,
            'date': article.publish_date.strftime('%b %d, %Y'),
            'readTime': article.estimated_read_time or f"{article.reading_time} min",
            'category': article.category,
            'subtopic': article.subtopic,
            'category_display': article.get_category_display(),
            'subtopic_display': article.get_subtopic_display(),
        })
    
    return JsonResponse({'recent_articles': data})

def redirect_reading_subtopic(request, subtopic):
    """
    Redirect from old reading/subtopic.html to new reading/subtopic/
    """
    return redirect(f'/reading/complex-systems/{subtopic}/', permanent=True)

def redirect_reading_subtopic_html(request, subtopic):
    """
    Redirect from old reading_ideas/subtopic.html to new reading/subtopic/
    Handles: reading_ideas/complex-systems.html -> /reading/complex-systems/
    """
    # Remove .html extension if present
    if subtopic.endswith('.html'):
        subtopic = subtopic[:-5]
    
    # Handle index.html specially
    if subtopic == 'index':
        return redirect('reading', permanent=True)
    
    return redirect(f'/reading/{subtopic}/', permanent=True)

# ========== UTILITY VIEWS ==========

# Context processor for social media links (available in all templates)
def social_media_context(request):
    """Make social media profiles available in all templates"""
    try:
        footer_profiles = SocialMediaProfile.objects.filter(
            is_active=True, 
            show_in_footer=True
        ).order_by('order')
        
        sidebar_profiles = SocialMediaProfile.objects.filter(
            is_active=True, 
            show_in_sidebar=True
        ).order_by('order')
        
        # Get site settings
        site_settings = SiteSettings.load()
        
        return {
            'social_media_footer': footer_profiles,
            'social_media_sidebar': sidebar_profiles,
            'social_media_profiles': SocialMediaProfile.objects.filter(is_active=True).order_by('order'),
            'site_settings': site_settings,
        }
    except:
        # Return empty context if database tables don't exist yet
        return {
            'social_media_footer': [],
            'social_media_sidebar': [],
            'social_media_profiles': [],
            'site_settings': None,
        }

# Custom error pages
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

# Search functionality
def search(request):
    """Search across all content"""
    query = request.GET.get('q', '')
    results = {
        'books': [],
        'articles': [],
        'talks': [],
        'themes': [],
    }
    
    if query:
        results['books'] = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(subtitle__icontains=query) | 
            Q(description__icontains=query)
        )[:10]
        
        results['articles'] = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            status='published',
            publish_date__lte=timezone.now()
        )[:10]
        
        results['talks'] = Talk.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )[:10]
        
        results['themes'] = Theme.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:10]
    
    social_profiles = SocialMediaProfile.objects.filter(is_active=True, show_in_footer=True)
    
    return render(request, 'search.html', {
        'query': query,
        'results': results,
        'social_media_profiles': social_profiles,
    })

# ========== DEBUG VIEWS ==========

def debug_articles(request):
    """Debug view to check article data"""
    articles = Article.objects.all()
    
    debug_info = []
    for article in articles:
        debug_info.append({
            'title': article.title,
            'status': article.status,
            'publish_date': article.publish_date,
            'is_past': article.publish_date <= timezone.now() if article.publish_date else False,
            'category': article.category,
            'subtopic': article.subtopic,
            'themes': [theme.name for theme in article.themes.all()],
        })
    
    return JsonResponse({
        'total_articles': articles.count(),
        'published_articles': articles.filter(status='published').count(),
        'articles_with_future_dates': articles.filter(
            status='published',
            publish_date__gt=timezone.now()
        ).count(),
        'articles_should_show': articles.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).count(),
        'articles': debug_info
    })