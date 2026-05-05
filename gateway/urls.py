from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    # MAIN NAVIGATION
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('reading/', views.reading_list, name='reading_list'),
    path('listening/', views.listening, name='listening'),
    path('books/', views.book_list, name='book_list'),
    
    # DETAIL PAGES
    path('reading/<slug:slug>/', views.reading_idea_detail, name='reading_idea_detail'),
    path('listening/<slug:slug>/', views.talk_detail, name='talk_detail'),
    path('books/<slug:slug>/', views.book_detail, name='book_detail'),
    path('talks/<slug:slug>/', views.talk_detail, name='talk_detail'),
    path('themes/<slug:slug>/', views.theme_detail, name='theme_detail'),

    # READING SUBTOPICS
    path('reading/<slug:subtopic>/', views.reading_subtopic, name='reading_subtopic'),

    # AUTHOR DASHBOARD
    path('author/dashboard/', views.author_dashboard, name='author_dashboard'),
    path('author/books/manage/', views.manage_books, name='manage_books'),
    path('author/books/upload/', views.upload_book, name='upload_book'),
    path('author/articles/manage/', views.manage_articles, name='manage_articles'),
    path('author/articles/upload/', views.upload_article, name='upload_article'),
    path('author/talks/manage/', views.manage_talks, name='manage_talks'),
    path('author/talks/upload/', views.upload_talk, name='upload_talk'),
    path('author/contact-messages/', views.manage_contact_messages, name='manage_contact_messages'),

    # NEWSLETTER & SEARCH
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('search/', views.search, name='search'),

    # API
    path('api/articles/', views.article_list_api, name='article_list_api'),
    path('api/article/<slug:slug>/', views.article_detail_api, name='article_detail_api'),

    # AUTH
    path('author/login/', auth_views.LoginView.as_view(template_name='auth/login.html', redirect_authenticated_user=True), name='login'),
    path('author/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Error handlers (Ensure these functions exist in your views.py)
handler404 = 'gateway.views.custom_404'
handler500 = 'gateway.views.custom_500'
