from django.urls import path
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    # ========== MAIN PAGES ==========
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('books/', views.book_list, name='book_list'),
    path('themes/', views.theme_list, name='theme_list'),
    path('media/', views.media, name='media'),
    path('contact/', views.contact, name='contact'),
    path('reading/', views.reading, name='reading'),
    path('listening/', views.listening, name='listening'),
    path('connect/', views.connect, name='connect'),
    
    # ========== ALIASES ==========
    path('articles/', views.reading, name='article_list'),
    path('talks/', views.listening, name='talk_list'),
    
    # ========== DETAIL PAGES ==========
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('themes/<slug:slug>/', views.theme_detail, name='theme_detail'),
    path('talks/<slug:slug>/', views.talk_detail, name='talk_detail'),
    
    # ========== READING SUBTOPIC PAGES ==========
    path('reading/complex-systems/', views.complex_systems, name='complex_systems'),
    path('reading/democracy-policy/', views.democracy_policy, name='democracy_policy'),
    path('reading/evolution-economics/', views.evolution_economics, name='evolution_economics'),
    path('reading/jobs-employment/', views.jobs_employment, name='jobs_employment'),
    path('reading/business-ethics/', views.business_ethics, name='business_ethics'),
    path('reading/purpose-lives/', views.purpose_lives, name='purpose_lives'),
    path('reading/listening-others/', views.listening_others, name='listening_others'),
    path('reading/future-india/', views.future_india, name='future_india'),
    
    # ========== ARTICLE DETAIL PAGES ==========
    # CRITICAL FIX: Add reading_idea_detail pattern
    path('reading/idea/<slug:slug>/', views.reading_idea_detail, name='reading_idea_detail'),
    
    # Alternative article detail patterns
    path('article/<slug:slug>/', views.reading_idea_detail, name='article_detail'),
    path('articles/<slug:slug>/', views.reading_idea_detail, name='article_detail_alt'),
    path('reading/article/<slug:slug>/', views.reading_idea_detail, name='reading_article_detail'),
    
    # ========== GENERIC READING SUBTOPIC ==========
    path('reading/<str:subtopic>/', views.reading_subtopic, name='reading_subtopic'),
    
    # ========== NEWSLETTER ==========
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # ========== AUTHOR DASHBOARD ==========
    path('author/dashboard/', views.author_dashboard, name='author_dashboard'),
    
    # Book management
    path('author/books/upload/', views.upload_book, name='upload_book'),
    path('author/books/manage/', views.manage_books, name='manage_books'),
    path('author/books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('author/books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    
    # Article management
    path('author/articles/upload/', views.upload_article, name='upload_article'),
    path('author/articles/manage/', views.manage_articles, name='manage_articles'),
    
    # Talk management
    path('author/talks/upload/', views.upload_talk, name='upload_talk'),
    path('author/talks/manage/', views.manage_talks, name='manage_talks'),
    
    # Simple upload forms
    path('author/upload/reading/', views.upload_reading, name='upload_reading'),
    path('author/upload/listening/', views.upload_listening, name='upload_listening'),
    
    # Contact messages
    path('author/contact-messages/', views.manage_contact_messages, name='manage_contact_messages'),
    path('author/mark-message-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    
    # ========== SEARCH ==========
    path('search/', views.search, name='search'),
    
    # ========== API ENDPOINTS ==========
    path('api/articles/', views.article_list_api, name='article_list_api'),
    path('api/articles/recent/', views.recent_articles_api, name='recent_articles_api'),
    path('api/articles/<str:subtopic>/', views.articles_by_subtopic_api, name='articles_by_subtopic_api'),
    path('api/article/<slug:slug>/', views.article_detail_api, name='article_detail_api'),
    
    # ========== DEBUG ENDPOINTS ==========
    path('debug/articles/', views.debug_articles, name='debug_articles'),
    
    # ========== REDIRECTS FOR LEGACY URLS ==========
    path('reading_ideas/', RedirectView.as_view(pattern_name='reading', permanent=True)),
    path('reading_ideas/<str:subtopic>/', views.redirect_reading_subtopic, name='redirect_reading_subtopic'),
    path('reading_ideas/<str:subtopic>.html', views.redirect_reading_subtopic_html, name='redirect_reading_subtopic_html'),
    
    # ========== PWA FILES ==========
    path('sw.js', 
         RedirectView.as_view(url=staticfiles_storage.url('js/sw.js')), 
         name='service_worker'),
    path('manifest.webmanifest', 
         RedirectView.as_view(url=staticfiles_storage.url('manifest.webmanifest')), 
         name='manifest'),
    
    # ========== EXTERNAL API ENDPOINTS ==========
    path('m/api/reamaze/v2/customers/auth', 
         lambda request: JsonResponse({'auth': False}), 
         name='reamaze_auth'),
    path('markup/ad', 
         lambda request: HttpResponse('', content_type='text/html'), 
         name='ad_markup'),
    
    # ========== AUTHENTICATION ==========
    path('author/login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('author/logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('custom-login/', views.custom_login, name='custom_login'),
    path('custom-logout/', views.custom_logout, name='custom_logout'),
]

# Error handlers
handler404 = 'gateway.views.custom_404'
handler500 = 'gateway.views.custom_500'