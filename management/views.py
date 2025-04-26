from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EmployerRegistrationForm
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'management/home.html')

@login_required
def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/employer/success/')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'management/employer_register.html', {'form': form})

@login_required
def registration_success(request):
    return render(request, 'management/success.html')
