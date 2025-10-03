from django.urls import path
from . import views

app_name = 'subscriptions' 

urlpatterns = [
    path('plans/', views.plan_list, name='plan_list'),
    path('manage_plan/', views.manage_plans, name='manage_plans'),
    path('purchase/<int:plan_id>/', views.purchase_plan, name='purchase_plan'),
]