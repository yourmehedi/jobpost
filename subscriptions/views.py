from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Plan, Subscription
from accounts.models import CustomUser

@login_required
def plan_list(request):
    weekly_plans = Plan.objects.filter(duration='week')
    monthly_plans = Plan.objects.filter(duration='month')
    yearly_plans = Plan.objects.filter(duration='year')

    user_subscription = Subscription.objects.filter(user=request.user, active=True).first()

    return render(request, 'plan/plan_list.html', {
        'weekly_plans': weekly_plans,
        'monthly_plans': monthly_plans,
        'yearly_plans': yearly_plans,
        'user_subscription': user_subscription,
    })



@login_required
def purchase_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    user = request.user

    Subscription.objects.filter(user=user, active=True).update(active=False)  # আগে ছিল employer

    duration_map = {
        'week': timedelta(weeks=1),
        'month': timedelta(days=30),
        'year': timedelta(days=365),
    }

    start_date = timezone.now()
    end_date = start_date + duration_map.get(plan.duration, timedelta(days=30))

    Subscription.objects.create(
        user=user,  # আগে ছিল employer
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        active=True
    )

    user.has_ai_access = plan.has_ai_access
    user.save()

    messages.success(request, f"You have successfully subscribed to the {plan.name} plan!")
    return render(request, 'plan/purchase_success.html', {'plan': plan, 'end_date': end_date})
