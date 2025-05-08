from django.shortcuts import render, redirect
from .forms import EmployerRegistrationForm
from .models import EmployerProfile
from django.contrib.auth.decorators import login_required

def employer_register(request):
    try:
        existing = EmployerProfile.objects.get(user=request.user)
        return redirect('dashboard')  # Already registered
    except EmployerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            employer = form.save(commit=False)
            employer.user = request.user
            employer.save()
            return redirect('dashboard')
    else:
        form = EmployerRegistrationForm()

    return render(request, 'employers/employer_register.html', {'form': form})
