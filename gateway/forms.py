from django import forms
from django.core.validators import FileExtensionValidator
from .models import Book, Article, Talk, Theme

class BookUploadForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'description', 
            'cover_image', 'publisher', 'publication_year',
            'amazon_link', 'goodreads_link', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900, 
                'max': 2100
            }),
            'amazon_link': forms.URLInput(attrs={'class': 'form-control'}),
            'goodreads_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'cover_image': 'Upload book cover image (recommended: 300x450 pixels)',
            'is_featured': 'Check to display this book on the homepage',
        }
    
    def clean_publication_year(self):
        year = self.cleaned_data['publication_year']
        if year < 1900 or year > 2100:
            raise forms.ValidationError("Please enter a valid year between 1900 and 2100.")
        return year
    
    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image', False)
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            return image
        return image

class ArticleForm(forms.ModelForm):
    themes = forms.ModelMultipleChoiceField(
        queryset=Theme.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'content', 'excerpt', 'themes',
            'external_link', 'document', 'featured_image',
            'status', 'publish_date', 'reading_time'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Brief summary of the article (optional)'
            }),
            'content': forms.Textarea(attrs={
                'rows': 15, 
                'class': 'form-control',
                'placeholder': 'Write your article here...'
            }),
            'external_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/article'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'publish_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'reading_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Estimated reading time in minutes'
            }),
        }
        help_texts = {
            'slug': 'URL-friendly version of title (auto-generated if left blank)',
            'content': 'You can use basic HTML tags like <strong>, <em>, <a>, <ul>, <li>',
            'document': 'Optional PDF or document file',
            'featured_image': 'Optional featured image for the article',
            'publish_date': 'Leave blank to publish immediately',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make slug field not required if auto-generated
        self.fields['slug'].required = False
        # Make publish_date field not required
        self.fields['publish_date'].required = False
    
    def clean_document(self):
        document = self.cleaned_data.get('document', False)
        if document:
            # Validate file extension
            valid_extensions = ['pdf', 'doc', 'docx', 'txt']
            import os
            ext = os.path.splitext(document.name)[1][1:].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}'
                )
            
            # Validate file size (10MB limit)
            if document.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File too large ( > 10MB )")
        return document
    
    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image', False)
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
        return image

class TalkForm(forms.ModelForm):
    themes = forms.ModelMultipleChoiceField(
        queryset=Theme.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Talk
        fields = [
            'title', 'slug', 'description', 'media_type',
            'media_file', 'external_link', 'thumbnail',
            'themes', 'event_name', 'event_date', 'duration',
            'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 5, 
                'class': 'form-control'
            }),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'external_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... or https://vimeo.com/...'
            }),
            'event_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., TED Talk, Conference Name, Interview Series'
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HH:MM:SS format (e.g., 01:15:30 for 1 hour 15 minutes 30 seconds)'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'slug': 'URL-friendly version of title (auto-generated if left blank)',
            'media_file': 'Upload audio/video file (max 500MB)',
            'external_link': 'YouTube, Vimeo, or other external link',
            'thumbnail': 'Thumbnail image for the talk',
            'duration': 'Leave blank if unknown',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make slug field not required if auto-generated
        self.fields['slug'].required = False
        # Make event_date and duration not required
        self.fields['event_date'].required = False
        self.fields['duration'].required = False
    
    def clean_media_file(self):
        media_file = self.cleaned_data.get('media_file', False)
        if media_file:
            # Validate file extension
            valid_extensions = ['mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'm4a']
            import os
            ext = os.path.splitext(media_file.name)[1][1:].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}'
                )
            
            # Validate file size (500MB limit)
            if media_file.size > 500 * 1024 * 1024:
                raise forms.ValidationError("File too large ( > 500MB )")
        return media_file
    
    def clean_external_link(self):
        external_link = self.cleaned_data.get('external_link', '')
        if external_link:
            # Check if it's a valid URL
            from django.core.validators import URLValidator
            from django.core.exceptions import ValidationError
            
            val = URLValidator()
            try:
                val(external_link)
            except ValidationError:
                raise forms.ValidationError("Please enter a valid URL")
            
            # Check if it's a YouTube or Vimeo link for better validation
            if 'youtube.com' not in external_link and 'youtu.be' not in external_link and 'vimeo.com' not in external_link:
                # Warn but don't reject non-YouTube/Vimeo links
                pass
                
        return external_link
    
    def clean_duration(self):
        duration = self.cleaned_data.get('duration', '')
        if duration:
            try:
                # Parse duration string like "01:15:30"
                parts = duration.split(':')
                if len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    if hours < 0 or minutes < 0 or seconds < 0 or minutes >= 60 or seconds >= 60:
                        raise forms.ValidationError("Invalid duration format. Use HH:MM:SS")
                elif len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    if minutes < 0 or seconds < 0 or seconds >= 60:
                        raise forms.ValidationError("Invalid duration format. Use MM:SS or HH:MM:SS")
                else:
                    raise forms.ValidationError("Invalid duration format. Use HH:MM:SS or MM:SS")
            except ValueError:
                raise forms.ValidationError("Invalid duration format. Use numbers for HH:MM:SS")
        
        return duration

class ContactForm(forms.Form):
    """Contact form for the website"""
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('speaking', 'Speaking Engagement'),
        ('media', 'Media Inquiry'),
        ('academic', 'Academic/Research'),
        ('editorial', 'Editorial Inquiry'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    
    organization = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your organization (optional)'
        })
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        initial='general',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...'
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message.strip()) < 10:
            raise forms.ValidationError("Please provide a more detailed message.")
        return message

class NewsletterSignupForm(forms.Form):
    """Newsletter signup form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name (optional)'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if email is already subscribed and active
        from .models import NewsletterSubscriber
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            if subscriber.is_active:
                raise forms.ValidationError("This email is already subscribed.")
        except NewsletterSubscriber.DoesNotExist:
            pass
        return email

class SearchForm(forms.Form):
    """Search form"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books, articles, talks...'
        })
    )