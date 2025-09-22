from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    GOOD EXAMPLE: Clean User model with Single Responsibility
    
    Responsibility: User Authentication & Basic Identity
    - Only handles authentication-related fields
    - Minimal, focused scope
    - No business logic mixed in
    """
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users_user'

    def __str__(self):
        return f"{self.username} ({self.email})"


class UserProfile(models.Model):
    """
    GOOD EXAMPLE: Separate model for Profile Information
    
    Responsibility: User Profile Data Management
    - Personal information only
    - Contact details
    - Profile-specific fields
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        null=True, 
        blank=True
    )
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Profile Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user_profile'

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def has_complete_address(self):
        """Check if user has complete address information"""
        return all([
            self.address,
            self.city,
            self.country,
            self.postal_code
        ])


class UserPreferences(models.Model):
    """
    GOOD EXAMPLE: Separate model for User Preferences
    
    Responsibility: User Settings & Preferences Management
    - Notification preferences
    - Display preferences
    - Regional settings
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=True)
    newsletter_subscription = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Regional Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=10, default='USD')
    date_format = models.CharField(max_length=20, default='MM/DD/YYYY')
    
    # Display Preferences
    theme = models.CharField(
        max_length=20, 
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto')
        ],
        default='light'
    )
    items_per_page = models.PositiveIntegerField(default=20)
    
    # Privacy Preferences
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('friends', 'Friends Only')
        ],
        default='public'
    )
    show_online_status = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user_preferences'

    def __str__(self):
        return f"Preferences of {self.user.username}"


class UserAnalytics(models.Model):
    """
    GOOD EXAMPLE: Separate model for Analytics Data
    
    Responsibility: User Analytics & Tracking
    - Login statistics
    - Profile metrics
    - Activity tracking
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    # Login Analytics
    login_count = models.PositiveIntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_user_agent = models.TextField(blank=True)
    
    # Profile Analytics
    profile_views = models.PositiveIntegerField(default=0)
    profile_completion_score = models.FloatField(default=0.0)
    
    # Activity Analytics
    total_sessions = models.PositiveIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    
    # Engagement Analytics
    last_activity_date = models.DateTimeField(null=True, blank=True)
    days_since_registration = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user_analytics'

    def __str__(self):
        return f"Analytics of {self.user.username}"


class UserBusinessInfo(models.Model):
    """
    GOOD EXAMPLE: Separate model for Business Logic
    
    Responsibility: Business-related User Information
    - Premium membership
    - Account balance
    - Referral system
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='business_info'
    )
    
    # Premium Membership
    is_premium = models.BooleanField(default=False)
    premium_expires = models.DateTimeField(null=True, blank=True)
    premium_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise')
        ],
        null=True,
        blank=True
    )
    
    # Financial Information
    account_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    total_spent = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Referral System
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='referrals'
    )
    referral_earnings = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    # Account Status
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('pending', 'Pending Verification'),
            ('closed', 'Closed')
        ],
        default='active'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_user_business_info'

    def __str__(self):
        return f"Business Info of {self.user.username}"


class UserSession(models.Model):
    """
    GOOD EXAMPLE: Separate model for Session Management
    
    Responsibility: User Session Tracking
    - Session information only
    - No analytics mixed in
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Session Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'users_user_session'
        ordering = ['-last_activity']

    def __str__(self):
        return f"Session {self.session_key} for {self.user.username}"


# GOOD EXAMPLE: Using Django signals to auto-create related models
@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    """
    Automatically create related models when a User is created
    
    This ensures every User has all related models without
    cluttering the User model with this logic
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
        UserPreferences.objects.get_or_create(user=instance)
        UserAnalytics.objects.get_or_create(user=instance)
        UserBusinessInfo.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_related_models(sender, instance, **kwargs):
    """
    Save related models when User is saved
    
    Ensures related models exist and are saved properly
    """
    # Get or create related models if they don't exist
    if hasattr(instance, 'profile'):
        instance.profile.save()
    
    if hasattr(instance, 'preferences'):
        instance.preferences.save()
    
    if hasattr(instance, 'analytics'):
        instance.analytics.save()
    
    if hasattr(instance, 'business_info'):
        instance.business_info.save()