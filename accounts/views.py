from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from urllib.parse import urlencode
from django.conf import settings
from jobseekers.models import *
from .models import CustomUser
from employers.models import *
User = get_user_model()
from .forms import *   
import requests


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def google_login(request):
#     code = request.data.get('code')
#     if not code:
#         return Response({'error': 'Code is required'}, status=400)
 # djkefnlwkefew
#     data = {
#         'code': code,
#         'client_id': settings.GOOGLE_CLIENT_ID,
#         'client_secret': settings.GOOGLE_CLIENT_SECRET,
#         'redirect_uri': settings.GOOGLE_REDIRECT_URI,
#         'grant_type': 'authorization_code',
#     }

#     token_response = requests.post('https://oauth2.googleapis.com/token', data=data)
#     token_json = token_response.json()
#     access_token = token_json.get('access_token')
#     id_token = token_json.get('id_token')

#     if not id_token:
#         return Response({'error': 'ID token not provided'}, status=400)

#     user_info_response = requests.get(
#         'https://www.googleapis.com/oauth2/v3/userinfo',
#         headers={'Authorization': f'Bearer {access_token}'}
#     )
#     user_info = user_info_response.json()

#     email = user_info.get('email')
#     name = user_info.get('name')
#     picture = user_info.get('picture')

#     if not email:
#         return Response({'error': 'Email not available'}, status=400)

#     user, created = CustomUser.objects.get_or_create(email=email, defaults={
#         'name': name,
#         'is_verified': True,
#         'auth_provider': 'google',
#     })

#     if created and picture:
#         download_image(picture, user)

#     refresh = get_tokens_for_user(user)

#     return Response({
#         'refresh': str(refresh['refresh']),
#         'access': str(refresh['access']),
#     })

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def download_image(url, user):
    response = requests.get(url)
    if response.status_code == 200:
        file_name = url.split("/")[-1]
        user.image.save(file_name, ContentFile(response.content))
        user.save()

@api_view(['GET'])
def user_profile(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            'name': user.username,
            'email': user.email,
            'profile_image': user.image.url if user.image else None,
        })
    else:
        return Response({'error': 'User not authenticated'}, status=401)

def logout_view(request):
    return render(request, 'accounts/logout.html')

def jobseeker_register(request):
    if request.method == 'POST':
        # Basic user info
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Jobseeker additional info
        full_name = request.POST.get('full_name')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        job_type_preference = request.POST.get('job_type_preference')
        preferred_country = request.POST.get('preferred_country')
        preferred_city = request.POST.get('preferred_city')
        passport_number = request.POST.get('passport_number')
        national_id = request.POST.get('national_id')
        document_upload = request.FILES.get('document_upload')
        
        print(username, email, password, password2, full_name, date_of_birth, 
              gender, date_of_birth, contact_number, address, job_type_preference, 
              preferred_city, preferred_country, passport_number, national_id, document_upload)
        # Validation
        if not all([username, email, password, password2, full_name, date_of_birth, gender, contact_number, address]):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'accounts/jobseeker_regis.html', {'role': 'Job Seeker'})

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/jobseeker_regis.html', {'role': 'Job Seeker'})

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'accounts/jobseeker_regis.html', {'role': 'Job Seeker'})

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/jobseeker_regis.html', {'role': 'Job Seeker'})

        # Create user
        user = CustomUser.objects.create_user(username=username, email=email, password=password, user_type='jobseeker')
        
        # Create jobseeker profile
        Jobseeker.objects.create(
            user=user,
            full_name=full_name,
            date_of_birth=date_of_birth,
            gender=gender,
            contact_number=contact_number,
            address=address,
            email=email,
            job_type_preference=job_type_preference,
            preferred_country=preferred_country,
            preferred_city=preferred_city,
            passport_number=passport_number,
            national_id=national_id,
            document_upload=document_upload
        )

        messages.success(request, 'Account created successfully!')
        return redirect('accounts:login')

    return render(request, 'accounts/jobseeker_regis.html', {'role': 'Job Seeker'})

def employer_register(request):
    if request.method == 'POST':
        form = EmployerFullRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False  # Admin approval pending
            user.save()

            EmployerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                employer_type=form.cleaned_data['employer_type'],
                company_website=form.cleaned_data.get('company_website'),
                license_number=form.cleaned_data.get('license_number'),
                license_file=form.cleaned_data.get('license_file'),
                official_address=form.cleaned_data.get('official_address'),
                contact_number=form.cleaned_data.get('contact_number'),
                tin=form.cleaned_data.get('tin')
            )

            messages.info(request, "Registration successful. Please wait for admin approval.")
            return redirect('accounts:login')
    else:
        form = EmployerFullRegisterForm()

    return render(request, 'accounts/employer_regis.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)

        if user:
            # ✅ Only check approval for employer
            if getattr(user, 'user_type', None) == 'employer' and getattr(user, 'is_approved', False) is False:
                messages.warning(request, 'Your account is pending admin approval.')
                return render(request, 'accounts/login.html')

            login(request, user)

            if user.is_superuser or getattr(user, 'user_type', None) == 'superadmin':
                return redirect('management:dashboard')
            elif getattr(user, 'user_type', None) == 'employer':
                return redirect('employers:dashboard')
            elif getattr(user, 'user_type', None) == 'jobseeker':
                return redirect('jobseeker:dashboard')
            else:
                messages.error(request, 'Unknown user type.')
                return render(request, 'accounts/login.html')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")
            return redirect("accounts:forgot_password")

        # Token তৈরি করে Reset URL বানানো
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(f"/accounts/reset/{uid}/{token}/")

        # ইমেইল পাঠানো
        subject = "Password Reset Request"
        message = render_to_string("accounts/password_reset_email.html", {
            "user": user,
            "reset_link": reset_link,
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        messages.success(request, "A password reset link has been sent to your email.")
        return redirect("accounts:login")

    return render(request, "accounts/forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect(request.path)

            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful. You can now log in.")
            return redirect("accounts:login")

        return render(request, "accounts/reset_password.html", {"validlink": True})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return render(request, "accounts/reset_password.html", {"validlink": False})

def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("No code provided", status=400)

    # --- Get access token ---
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    r = requests.post(token_url, data=data)
    token_data = r.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return HttpResponse("Failed to obtain access token", status=400)

    # --- Get user info from Google ---
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": access_token}
    user_info = requests.get(user_info_url, params=params).json()

    email = user_info.get("email")
    name = user_info.get("name", email)

    if not email:
        return HttpResponse("Failed to fetch user info", status=400)

    # --- Get the saved user_type from session (default jobseeker) ---
    user_type = request.session.get("pending_user_type", "jobseeker")

    # --- Create or get user ---
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "first_name": name.split(" ")[0] if name else "",
            "last_name": " ".join(name.split(" ")[1:]) if name and len(name.split(" ")) > 1 else "",
            "user_type": user_type,
            "is_verified": True,
            "is_approved": True if user_type == "employer" else False,  # employers auto-approved or manual later
        },
    )

    # --- Login user ---
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    # --- Create or update profile based on user_type ---
    if user_type == "jobseeker":
        jobseeker, _ = Jobseeker.objects.get_or_create(user=user)
        jobseeker.full_name = name
        jobseeker.email = email
        if not jobseeker.gender:
            jobseeker.gender = "other"
        if not jobseeker.contact_number:
            jobseeker.contact_number = "N/A"
        jobseeker.save()

    elif user_type == "employer":
        from employers.models import EmployerProfile
        employer, _ = EmployerProfile.objects.get_or_create(user=user)
        employer.company_name = name or "Unnamed Company"
        employer.email = email
        employer.save()

    # --- Clear session data ---
    if "pending_user_type" in request.session:
        del request.session["pending_user_type"]

    return redirect("/")



# Facebook login system section
def facebook_login(request):
    params = {
        "client_id": settings.FACEBOOK_CLIENT_ID,
        "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        "scope": "email,public_profile",
        "response_type": "code",
        "auth_type": "rerequest",  # re-request permissions if needed
    }
    url = "https://www.facebook.com/v16.0/dialog/oauth?" + urlencode(params)
    return redirect(url)

def fetch_facebook_access_token(code):
    token_url = "https://graph.facebook.com/v16.0/oauth/access_token"
    params = {
        "client_id": settings.FACEBOOK_CLIENT_ID,
        "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        "client_secret": settings.FACEBOOK_CLIENT_SECRET,
        "code": code,
    }
    resp = requests.get(token_url, params=params)
    return resp.json()

def facebook_callback(request):

    code = request.GET.get("code")
    if not code:
        return HttpResponse("No code provided", status=400)

    token_data = fetch_facebook_access_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        return HttpResponse("Failed to obtain Facebook access token: " + str(token_data), status=400)

    # Fetch user info from Graph API
    # fields can include: id,name,email,picture{url}
    user_info_url = "https://graph.facebook.com/me"
    params = {"fields": "id,name,email,picture.width(400).height(400)", "access_token": access_token}
    user_info_resp = requests.get(user_info_url, params=params)
    user_info = user_info_resp.json()

    email = user_info.get("email")
    name = user_info.get("name", "")
    picture_url = None
    try:
        picture_url = user_info.get("picture", {}).get("data", {}).get("url")
    except Exception:
        picture_url = None

    # Facebook sometimes does not provide email (user may have none or blocked). Handle gracefully.
    if not email:
        # Option A: ask user to provide email (redirect to a page)
        # For now, return an error message
        return HttpResponse("Facebook account did not provide an email. Please sign up with email.", status=400)

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "first_name": name.split(" ")[0] if name else "",
            "last_name": " ".join(name.split(" ")[1:]) if name and len(name.split(" ")) > 1 else "",
            "user_type": "jobseeker",
        },
    )

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    # Update/create Jobseeker profile (same logic as Google)
    jobseeker, _ = Jobseeker.objects.get_or_create(user=user)
    if name:
        jobseeker.full_name = name
    jobseeker.email = email
    if picture_url:
        try:
            pic_resp = requests.get(picture_url)
            if pic_resp.status_code == 200:
                jobseeker.document_upload.save(f"{user.username}_fb.jpg", ContentFile(pic_resp.content), save=False)
        except Exception:
            pass

    if not jobseeker.gender:
        jobseeker.gender = "other"
    if not jobseeker.contact_number:
        jobseeker.contact_number = ""
    jobseeker.save()

    return redirect("/")

# def user_select(request):
#     return render(request, 'accounts/user_select.html')

# def user_select_fb(request):
#     return render(request, 'accounts/user_select_fb.html')




def choose_user_type(request):
    if request.method == "POST":
        user_type = request.POST.get("user_type")

        if user_type not in ["jobseeker", "employer"]:
            messages.error(request, "Please select a valid role.")
            return redirect("choose_user_type")

        # Save temporarily in session
        request.session["pending_user_type"] = user_type

        # Redirect to Google login, NOT callback
        return redirect("accounts:google_login")

    return render(request, "accounts/choose_user_type.html")

def google_login(request):
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&scope=email%20profile"
    )
    return redirect(google_auth_url)