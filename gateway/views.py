from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .forms import ArticleForm
import re
from django.contrib import messages, admin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from .models import (
    Book, Theme, GatewayPage, SocialMediaProfile, 
    ContactMessage, NewsletterSubscriber, Article, Talk
)

# ========== PUBLIC VIEWS ==========

def home(request):
    page = GatewayPage.objects.filter(page_type='home').first()
    
    # Existing logic for snippets
    featured_books = Book.objects.filter(is_featured=True)[:3]
    recent_articles = Article.objects.filter(
        status='published', category='READ'
    ).order_by('-publish_date')[:3]
    
    # New logic for the Thematic Gateway
    # This groups themes by Arun's "buckets"
    themes_by_bucket = {
        'system': Theme.objects.filter(bucket='system'),
        'me_us': Theme.objects.filter(bucket='me_us'),
        'future_india': Theme.objects.filter(bucket='future_india'),
    }
    
    return render(request, 'home.html', {
        'page': page,
        'featured_books': featured_books,
        'recent_articles': recent_articles,
        'themes': themes_by_bucket,
    })

def about(request):
    # Fetch the About page content from the database
    about_page = get_object_or_404(GatewayPage, page_type='about')
    
    # Fetch the most recently published book
    latest_book = Book.objects.order_by('-publication_year').first()
    
    context = {
        'about_page': about_page,
        'latest_book': latest_book,
    }
    return render(request, 'about.html', context)

def social_media_context(request):
    """
    REQUIRED by settings.py context_processors.
    This makes 'social_media_profiles' available to EVERY template automatically.
    """
    return {
        'social_media_profiles': SocialMediaProfile.objects.filter(is_active=True).order_by('order')
    }

def contact(request):
    # Fetch content for the contact page
    contact_page = GatewayPage.objects.filter(page_type='contact').first()
    social_links = SocialMediaProfile.objects.filter(is_active=True).order_by('order')
    
    if request.method == 'POST':
        # Processing the form submission
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')

    return render(request, 'contact.html', {
        'contact_page': contact_page,
        'social_links': social_links
    })

def reading_list(request):
    # Articles now handle only reading content
    articles = Article.objects.filter(category='READ', status='published').order_by('-publish_date')
    return render(request, 'reading.html', {'articles': articles})


def listening(request):
    # Fetch the page SEO/Header info
    page = GatewayPage.objects.filter(page_type='listening').first()
    
    # Strictly use the Talk model for the listening section
    videos = Talk.objects.all().order_by('-event_date', '-created_at')
    
    # Note: No loop needed here because Talk.youtube_id is now a @property in models.py
    return render(request, 'listening.html', {'page': page, 'videos': videos})

def talk_detail(request, slug):
    # Fetch the specific talk using the slug
    talk = get_object_or_404(Talk, slug=slug)
    return render(request, 'talk_detail.html', {'talk': talk})


def book_list(request):
    # 1. Fetch books sorted by year (newest first)
    books = Book.objects.all().order_by('-publication_year')
    
    # 2. Grab a featured book for a special spotlight section
    featured_book = Book.objects.filter(is_featured=True).first()
    
    # 3. Fetch the CMS settings for the 'books' page header/meta
    page = GatewayPage.objects.filter(page_type='books').first()
    
    context = {
        'books': books,
        'featured_book': featured_book,
        'page': page,
    }
    return render(request, 'books.html', context)

# ========== DETAIL VIEWS ==========

def reading_idea_detail(request, slug):
    # Fetch the specific article being viewed
    article = get_object_or_404(Article, slug=slug)
    
    # Fetch the 3 most recent published articles (excluding the current one)
    # Ordered by publish_date descending
    recent = Article.objects.filter(status='published').exclude(id=article.id).order_by('-publish_date')[:3]
    
    return render(request, 'reading_idea_detail.html', {
        'article': article, 
        'recent_posts': recent
    })

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    return render(request, 'book_detail.html', {'book': book})

def theme_detail(request, slug):
    theme = get_object_or_404(Theme, slug=slug)
    
    # This pulls everything "slotted" into this theme
    context = {
        'theme': theme,
        'articles': theme.article_set.all(),
        'books': theme.books.all(),
        'talks': theme.talk_set.all(),
    }
    return render(request, 'theme_detail.html', context)

# ========== DYNAMIC SUBTOPICS ==========

def reading_subtopic(request, subtopic):
    category_map = {
        'complex-systems': 'COMPLEX_SYSTEMS',
        'democracy-policy': 'DEMOCRACY_POLICY',
        'evolution-economics': 'EVOLUTION_ECONOMICS',
        'jobs-employment': 'JOBS_EMPLOYMENT',
        'business-ethics': 'BUSINESS_ETHICS',
        'purpose-lives': 'PURPOSE_LIVES',
        'listening-others': 'LISTENING_OTHERS',
        'future-india': 'FUTURE_INDIA',
    }
    db_category = category_map.get(subtopic, 'COMPLEX_SYSTEMS')
    articles = Article.objects.filter(category=db_category, status='published').order_by('-publish_date')
    return render(request, 'reading_subtopic.html', {
        'articles': articles, 
        'title': subtopic.replace('-', ' ').upper(),
        'subtopic': subtopic
    })

# ========== AUTHOR & MANAGEMENT VIEWS ==========

@login_required
def author_dashboard(request):
    context = {
        'book_count': Book.objects.count(),
        'article_count': Article.objects.filter(category='READ').count(),
        'video_count': Article.objects.filter(category='LISTEN').count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
    }
    return render(request, 'author/dashboard.html', context)

@login_required
def manage_books(request):
    books = Book.objects.all().order_by('-publication_year')
    return render(request, 'author/manage_books.html', {'books': books})

@login_required
def upload_book(request):
    return render(request, 'author/upload_book.html')

@login_required
def manage_articles(request):
    articles = Article.objects.filter(category='READ').order_by('-publish_date')
    return render(request, 'author/manage_articles.html', {'articles': articles})

@login_required
def upload_article(request):
    return render(request, 'author/upload_article.html')

@login_required
def manage_talks(request):
    talks = Article.objects.filter(category='LISTEN').order_by('-publish_date')
    return render(request, 'author/manage_talks.html', {'talks': talks})

@login_required
def upload_talk(request):
    return render(request, 'author/upload_talk.html')

@login_required
def manage_contact_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'author/manage_contact_messages.html', {'contact_messages': messages})

@login_required
def upload_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = "Arun Maira"  # Auto-assign author
            article.save()
            form.save_m2m() # Important for many-to-many fields like 'themes'
            messages.success(request, "Article uploaded successfully!")
            return redirect('manage_articles')
    else:
        form = ArticleForm()
    
    return render(request, 'author/upload_article.html', {'form': form})

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    
    # Check if empty
    if not email:
        return render(request, 'newsletter_success.html', {'status': 'error', 'message': 'Email is required.'})

    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'subscription_type': 'general', 'is_active': True}
        )

        if not created:
            if subscriber.is_active:
                status, message = 'info', 'You are already subscribed!'
            else:
                subscriber.is_active = True
                subscriber.save() 
                status, message = 'success', 'Welcome back! Subscription reactivated.'
        else:
            status, message = 'success', 'Thank you for joining our newsletter!'

    except ValidationError as e:
        # Pulls specific error from Model's clean() method
        status, message = 'error', e.message_dict.get('email', ['Invalid email'])[0]
    except Exception:
        status, message = 'error', 'An error occurred. Please try again.'

    # Always return the same template file for HTMX consistency
    return render(request, 'newsletter_success.html', {'status': status, 'message': message})

# ========== SEARCH & API & UTILS ==========

def search(request):
    query = request.GET.get('q', '')
    results = Article.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)) if query else []
    return render(request, 'search_results.html', {'results': results, 'query': query})

def article_list_api(request):
    articles = list(Article.objects.values('title', 'slug', 'category'))
    return JsonResponse({'articles': articles})

def article_detail_api(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return JsonResponse({'title': article.title, 'content': article.content})

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)


def health_check(request):
    """Simple view for server monitoring and load balancers"""
    return HttpResponse("OK")
