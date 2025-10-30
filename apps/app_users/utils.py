from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
import requests
import secrets
import string

def send_welcome_email(user_email, user_name):
    subject = "Welcome to Bloome! 🥳 "
    message = ''
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    html_body = render_to_string(
        "emails/welcome.html",
        {
            "user": user_name,
            "login_url": f"{settings.LIVE_SITE_URL_RN}{settings.LOGIN_URL}",
        }
    )

    send_mail(subject, 
              message, 
              from_email, 
              recipient_list,
              html_message=html_body,   
              )

def generate_random_username(base_name):
    # for enerate a unique username --->>
    User = get_user_model()
    base_name = base_name.lower().replace(' ', '').replace('.', '')
    
    if not User.objects.filter(username=base_name).exists():
        return base_name
    
    # random numbers if taken
    for _ in range(10):
        random_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
        username = f"{base_name}{random_suffix}"
        if not User.objects.filter(username=username).exists():
            return username
    
    # Fallback
    import time
    return f"{base_name}{int(time.time())}"

def generate_random_password():
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(12))

def fetch_google_profile(access_token):
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Google profile: {e}")
        return None

from django.utils.timezone import now
from datetime import timedelta

def create_user_from_google(google_profile, access_token, refresh_token, id_token, expires_in):
    User = get_user_model()
    
    google_email = google_profile.get('email')
    google_id = google_profile.get('id')
    
    user = User.objects.filter(email=google_email).first()
    
    if not user:
        username = generate_random_username(google_profile.get('given_name', 'user'))
        password = generate_random_password()
        
        user = User.objects.create_user(
            email=google_email,
            username=username,
            password=password
        )
        
        print(f"Created new user: {user.email}")
    
    # Update or create profile with Google data
    profile = user.profile
    
    # Update Google-specific fields
    profile.google_email = google_email
    profile.access_token = access_token
    profile.refresh_token = refresh_token
    profile.id_token = id_token
    profile.token_expiry = now() + timedelta(seconds=expires_in)
    profile.display_name = google_profile.get('name', '')
    profile.locale = google_profile.get('locale', '')
    profile.verified_email = google_profile.get('verified_email', False)
    
    # updating profile fields if they're empty ==>>
    if not profile.first_name:
        profile.first_name = google_profile.get('given_name', '')
    if not profile.last_name:
        profile.last_name = google_profile.get('family_name', '')
    
    # downloading and save profile picture if available ==>>
    if google_profile.get('picture') and not profile.profile_picture or profile.profile_picture.name == 'default.png':
        try:
            import urllib.request
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage
            import os
            
            picture_url = google_profile.get('picture')
            response = urllib.request.urlopen(picture_url)
            image_content = response.read()
            
            # Generate filename
            filename = f"google_profile_{user.uid}.jpg"
            
            # Save the image
            profile.profile_picture.save(
                filename,
                ContentFile(image_content),
                save=False
            )
        except Exception as e:
            print(f"Error downloading profile picture: {e}")
    
    profile.save()
    
    return user

def refresh_google_token(profile):
    if not profile.refresh_token:
        return False, "No refresh token available"
    
    try:
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": profile.refresh_token,
            "grant_type": "refresh_token"
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post("https://oauth2.googleapis.com/token", data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        
        # Update profile with new tokens
        profile.access_token = token_data["access_token"]
        profile.token_expiry = now() + timedelta(seconds=token_data["expires_in"])
        if "id_token" in token_data:
            profile.id_token = token_data["id_token"]
        profile.save()
        
        return True, "Token refreshed successfully"
        
    except Exception as e:
        return False, str(e)
