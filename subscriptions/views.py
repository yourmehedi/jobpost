from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import PlanForm
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

    Subscription.objects.filter(user=user, active=True).update(active=False) 

    duration_map = {
        'week': timedelta(weeks=1),
        'month': timedelta(days=30),
        'year': timedelta(days=365),
    }

    start_date = timezone.now()
    end_date = start_date + duration_map.get(plan.duration, timedelta(days=30))

    Subscription.objects.create(
        user=user, 
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        active=True
    )

    user.has_ai_access = plan.has_ai_access
    user.save()

    messages.success(request, f"You have successfully subscribed to the {plan.name} plan!")
    return render(request, 'plan/purchase_success.html', {'plan': plan, 'end_date': end_date})

@staff_member_required
def manage_plans(request):
    plans = Plan.objects.all()

    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        if plan_id:  # existing plan update
            plan = get_object_or_404(Plan, id=plan_id)
            form = PlanForm(request.POST, instance=plan)
        else:  # new plan create
            form = PlanForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("subscriptions:manage_plans")
    else:
        form = PlanForm()

    return render(request, "subscriptions/manage_plan.html", {
        "plans": plans,
        "form": form
    })

def plan_create(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plan_list')
    else:
        form = PlanForm()
    return render(request, 'plans/plan_form.html', {'form': form})

# প্ল্যান আপডেট করা
def plan_update(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('plan_list')
    else:
        form = PlanForm(instance=plan)
    return render(request, 'plans/plan_form.html', {'form': form})

# প্ল্যান ডিলিট করা
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == "POST":
        plan.delete()
        return redirect('plan_list')
    return render(request, 'plans/plan_confirm_delete.html', {'plan': plan})