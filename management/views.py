from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EmployerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, authenticate, login
from communications.models import Notification, Message
from employers.models import EmployerProfile
from subscriptions.models import *
from management.models import Employer
from accounts.forms import UserEditForm
from jobs.models import Job, JobApplication
from .models import *
from django.contrib import messages
from django.contrib import messages as dj_messages
from django.contrib.auth.decorators import user_passes_test
User = get_user_model()

def is_superadmin(user):
    return user.is_authenticated and user.is_superadmin 
 
@login_required
def home(request):
    print(request.user)
    return render(request, 'management/home.html')

@login_required
def reply_contact_message(request, pk):
    contact_msg = get_object_or_404(ContactMessage, pk=pk)

    if request.method == "POST":
        reply_text = request.POST.get("reply")
        now = timezone.now()

        # Send message to user's inbox
        if contact_msg.user: 
            Message.objects.create(
                sender=request.user,
                recipient=contact_msg.user,
                subject="Reply to your contact message",
                body=reply_text,
                sent_at=now
            )

            # Send notification
            Notification.objects.create(
                user=contact_msg.user,
                title="Reply to your contact message",
                message=reply_text[:250] + "..." if len(reply_text) > 250 else reply_text,
                link="/messages/inbox/",
                created_at=now,
                target_role="all"
            )

        dj_messages.success(request, "Reply sent successfully.")
        return redirect("management:contact_message_list")

    return render(request, "management/reply_contact_message.html", {"contact_msg": contact_msg})

@login_required
@user_passes_test(is_superadmin)
def contact_message_list(request):
    messages_list = ContactMessage.objects.select_related("user").order_by("-sent_at")
    return render(request, "management/contact_message_list.html", {"messages_list": messages_list})


@login_required
@user_passes_test(is_superadmin)
def delete_contact_message(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    dj_messages.success(request, "Message deleted successfully.")
    return redirect("management:contact_message_list")

@login_required
def contact_us(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message_text = request.POST.get("message")

        ContactMessage.objects.create(
            user=request.user, 
            name=name,
            email=email,
            message=message_text
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("management:contact_us")

    return render(request, 'management/contact_us.html')   

def privacy_policy(request):
    return render(request, 'management/privacy_policy.html')

def about_us(request):
    return render(request, 'management/about_us.html')

def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )

                Employer.objects.create(
                    user=user,
                    company_name=form.cleaned_data['company_name'],
                    company_website=form.cleaned_data['company_website'],
                    employer_type=form.cleaned_data['employer_type'],
                    license_file=form.cleaned_data.get('license_file')
                )

                return redirect('management:registration_success')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'management/employer_register.html', {'form': form})

def registration_success(request):
    return render(request, 'management/success.html')

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def dashboard_home(request):
    total_users = CustomUser.objects.count()
    employers = CustomUser.objects.filter(user_type="employer").count()
    jobseekers = CustomUser.objects.filter(user_type="jobseeker").count()
    applications = JobApplication.objects.count()

    context = {
        "total_users": total_users,
        "employers": employers,
        "jobseekers": jobseekers,
        "applications": applications,
    }
    return render(request, "management/dashboard_home.html", context)

def superuser_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('management:dashboard')  
            else:
                messages.error(request, 'you are not superuser!')
        else:
            messages.error(request, 'Username and password wrong!')

    return render(request, 'management/superuser_login.html')


@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def all_users(request):
    users = User.objects.all().order_by('-date_joined') 

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, id=user_id)

        if action == 'edit':
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, f"{user.username} updated successfully.")
                return redirect('management:all_users')
        elif action == 'activate':
            user.is_active = True
            user.save()
            messages.success(request, f"{user.username} activated.")
            return redirect('management:all_users')
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            messages.warning(request, f"{user.username} deactivated.")
            return redirect('management:all_users')
        elif action == 'delete':
            user.delete()
            messages.error(request, f"User deleted.")
            return redirect('management:all_users')
    else:
        edit_forms = {user.id: UserEditForm(instance=user).as_p() for user in users}
        return render(request, 'management/all_users.html', {
            'users': users,
            'edit_forms': edit_forms,
        })
     
    return render(request, 'management/all_users.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{user.username} updated successfully.")
            return redirect('management:all_users')  # redirect যেখানে লিস্ট দেখান হয়
    else:
        form = UserEditForm(instance=user)

    return render(request, 'management/edit_user.html', {
        'form': form,
        'user_obj': user,
    })

# @user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
# def all_users(request):
#     users = CustomUser.objects.all().order_by('-date_joined')

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         action = request.POST.get('action')
#         user = get_object_or_404(CustomUser, id=user_id)

#         if action == 'edit':
#             form = UserEditForm(request.POST, instance=user)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, f"{user.username} updated successfully.")
#                 return redirect('management:all_users')
#         elif action == 'activate':
#             user.is_active = True
#             user.save()
#             messages.success(request, f"{user.username} activated.")
#             return redirect('management:all_users')
#         elif action == 'deactivate':
#             user.is_active = False
#             user.save()
#             messages.warning(request, f"{user.username} deactivated.")
#             return redirect('management:all_users')
#         elif action == 'delete':
#             user.delete()
#             messages.error(request, f"User deleted.")
#             return redirect('management:all_users')
#     else:
#         edit_forms = {user.id: UserEditForm(instance=user).as_p() for user in users}
#         return render(request, 'management/all_users.html', {
#             'users': users,
#             'edit_forms': edit_forms,
#         })
    
@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def user_approval(request):
    users = User.objects.filter(is_active=False, is_superuser=False)
    return render(request, 'management/user_approval.html', {'users': users})

def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('user_approval') 

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def employer_verification(request):
    employers = EmployerProfile.objects.filter(is_approved=False)
    return render(request, 'management/employer_verification.html', {'employers': employers})

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def verify_employer(request, id):
    employer = get_object_or_404(EmployerProfile, id=id)
    employer.is_approved = True
    employer.save()

    # Approve user account too
    employer.user.is_approved = True
    employer.user.save()

    return redirect('management:employer_verification')

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def job_monitoring(request):
    jobs = Job.objects.all()
    
    return render(request, 'management/job_monitoring.html', {'jobs': jobs})


@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def review_user_jobs(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    jobs = Job.objects.filter(employer=employer)
    return render(request, 'management/review_user_jobs.html', {'employer': employer, 'jobs': jobs})

def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if job.status == 'active':
        job.status = 'closed'
    else:
        job.status = 'active'
    job.save()
    return redirect('management:job_monitoring')

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    return redirect('management:job_monitoring')

def ai_token_usage(request):
    premium_users = Subscription.objects.select_related('user', 'plan').filter(
        active=True,
        plan__has_ai_access=True
    )
    return render(request, 'management/ai_token_usage.html', {
        'premium_users': premium_users
    })


def subscription_history(request):
    if request.user.is_superuser:
        subscriptions = Subscription.objects.select_related('plan', 'user').all().order_by('-start_date')
    else:
        subscriptions = Subscription.objects.select_related('plan', 'user').filter(user=request.user).order_by('-start_date')
    
    return render(request, 'management/subscription_history.html', {
        'subscriptions': subscriptions,
    })

def delete_subscription(request, subscription_id):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete subscriptions.")
        return redirect('management:subscription_history')

    subscription = get_object_or_404(Subscription, id=subscription_id)
    subscription.delete()
    messages.success(request, "Subscription deleted successfully.")
    return redirect('management:subscription_history')