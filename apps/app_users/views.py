from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from urllib.parse import urlencode
import requests

from .forms import CommonRegistrationForm, ProfileForm
from .models import Profile, User
from .utils import send_welcome_email, generate_random_username, generate_random_password

def registration(request):
    if request.method == "POST":
        form = CommonRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            login(request, user)
            messages.success(request, "Register done!")

            try:
                send_welcome_email(user.email, user.username)
            except Exception as exc:
                print(f"Error sending welcome email: {exc}")
                
            messages.success(request, "Welcome to Bloome! Please complete your profile.")
            return redirect("signup_details")
    else:
        form = CommonRegistrationForm()

    return render(request, "auth/signup.html", {"form": form})

@login_required
def registration_step2(request):
    try:
        profile = request.user.profile
    except:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            the_form = form.save(commit=False)
            the_form.fill_up = True
            the_form.registered = True
            the_form.save()
            messages.success(request,"Congrats! Your account is complete.")
            return redirect("homepage")
        else:
            messages.error(request, form.errors)
    else:
        form = ProfileForm(instance=profile)
    
    context = {"form": form}
    return render(request, "auth/signup.html", context)

def logout_view(request):
    logout(request)
    return redirect("homepage")

def login_page(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already loggedIn !")
        return redirect("homepage")
    
    if request.POST:
        username_or_email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = authenticate(email=username_or_email, password=password)
            login(request, user)
            messages.success(request, "Log in success! Welcome.")

            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            
            return redirect("homepage")
        
        except Exception as e:
            messages.error(request,f"ERROR: {e}")
            messages.error(request,"May be credentials not valid!")

    return render(request, "auth/login.html")

def demo_login(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already loggedIn !")
        return redirect("homepage")
    
    email = "demo@gmail.com"
    password = "demo1234"

    user = authenticate(email=email, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, "Demo login success! Welcome.")
        return redirect("homepage")
    else:
        messages.error(request, "Demo login failed. Please try again.")
        return redirect("login_page")

# ===============  GOOGLE AUTH ===============

def google_login(request):
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }

    google_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return redirect(google_url)

def google_callback(request):
    code = request.GET.get("code")
    error = request.GET.get("error")

    if error:
        messages.error(request, "Google authentication failed.")
        return redirect("login_page")

    if not code:
        messages.error(request, "No authorization code received.")
        return redirect("login_page")

    try:
        # access token
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }

        token_response = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        token_json = token_response.json()
        
        access_token = token_json.get("access_token")
        if not access_token:
            messages.error(request, "Failed to get access token.")
            return redirect("login_page")

        # user info from Google
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
        google_user = user_response.json()

        email = google_user.get('email')
        first_name = google_user.get('given_name', '')
        last_name = google_user.get('family_name', '')
        picture = google_user.get('picture', '')

        # Check if user exists
        user = User.objects.filter(email=email).first()
        
        if not user:
            # Create new user
            username = generate_random_username(first_name or 'user')
            password = generate_random_password()
            
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password
            )

        # Update profile with Google data
        profile = user.profile
        if not profile.first_name:
            profile.first_name = first_name
        if not profile.last_name:
            profile.last_name = last_name
        if picture and not profile.profile_picture or profile.profile_picture.name == 'default.png':
            profile.google_email = email  # Store Google email
        
        profile.save()
        login(request, user)
        
        #  welcome email for new users ===>>>
        if not profile.registered:
            try:
                send_welcome_email(email, first_name or username)
            except Exception as e:
                print(f"Error sending welcome email: {e}")

        # Redirected based on profile completion --==--==>>>
        if not profile.fill_up or not profile.registered:
            messages.success(request, f"Welcome {first_name}! Please complete your profile.")
            return redirect("signup_details")
        else:
            messages.success(request, f"Welcome back, {first_name}!")
            return redirect("homepage")

    except Exception as e:
        print(f"Google auth error: {e}")
        messages.error(request, "Authentication failed. Please try again.")
        return redirect("login_page")
