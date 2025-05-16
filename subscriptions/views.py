from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Plan, Subscription
from accounts.models import CustomUser

def plan_list(request):
    plans = Plan.objects.all()
    return render(request, 'plan/plan_list.html', {'plans': plans})


@login_required
def purchase_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    # পুরোনো সাবস্ক্রিপশন বন্ধ করে দিচ্ছি
    Subscription.objects.filter(employer=request.user, active=True).update(active=False)

    # নতুন সাবস্ক্রিপশন তৈরি করছি
    Subscription.objects.create(
        employer=request.user,
        plan=plan,
        start_date=timezone.now(),
        active=True
    )

    # ইউজারের AI Access আপডেট করছি
    request.user.has_ai_access = plan.has_ai_access
    request.user.save()

    messages.success(request, f"You have successfully subscribed to the {plan.name} plan!")
    return render(request, 'plans/purchase_success.html', {'plan': plan})