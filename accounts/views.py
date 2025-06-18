
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .models import CustomUser
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from jobseekers.models import *
from employers.models import *
from .forms import *

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    code = request.data.get('code')
    if not code:
        return Response({'error': 'Code is required'}, status=400)

    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    token_response = requests.post('https://oauth2.googleapis.com/token', data=data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    id_token = token_json.get('id_token')

    if not id_token:
        return Response({'error': 'ID token not provided'}, status=400)

    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_info = user_info_response.json()

    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')

    if not email:
        return Response({'error': 'Email not available'}, status=400)

    user, created = CustomUser.objects.get_or_create(email=email, defaults={
        'name': name,
        'is_verified': True,
        'auth_provider': 'google',
    })

    if created and picture:
        download_image(picture, user)

    refresh = get_tokens_for_user(user)

    return Response({
        'refresh': str(refresh['refresh']),
        'access': str(refresh['access']),
    })

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
            'name': user.name,
            'email': user.email,
            'profile_image': user.image.url if user.image else None,
        })
    else:
        return Response({'error': 'User not authenticated'}, status=401)


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



def logout_view(request):
    return render(request, 'accounts/logout.html')
