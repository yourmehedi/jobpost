from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect 
from django.utils import timezone
from django.urls import reverse
from django.db import transaction
from django.contrib import messages as dj_messages
from django.contrib import messages
from accounts.models import CustomUser
from .models import Message, Notification, Broadcast


@login_required
def compose_message(request):
    if request.method == "POST":
        recipient_id = request.POST.get("recipient")
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        recipient = CustomUser.objects.get(id=recipient_id)

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            body=body
        )

        Notification.objects.create(
            user=recipient,
            title="New Message Received",
            message=f"You have a new message from {request.user.username}",
            link="/messages/inbox/",
            target_role="all"
        )

        return redirect("communications:inbox")

    if request.user.user_type == 'superadmin':
        users = CustomUser.objects.exclude(id=request.user.id)
    elif request.user.user_type == 'employer':
        users = CustomUser.objects.filter(user_type__in=['jobseeker', 'superadmin'])
    else:
        users = CustomUser.objects.filter(user_type__in=['employer', 'superadmin'])

    return render(request, "communications/compose_message.html", {"users": users})


@login_required
def inbox(request):
    msgs = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, "communications/inbox.html", {"messages": msgs})


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "communications/notifications.html", {"notifications": notifications})


def is_superadmin(user):
    return getattr(user, 'user_type', '') == 'superadmin'


@login_required
@user_passes_test(is_superadmin)
def broadcast_create(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        target_role = request.POST.get('target_role', 'all')
        specific_ids = request.POST.getlist('specific_recipients')

        if not subject or not body:
            dj_messages.error(request, "Subject and body are required.")
            return redirect('communications:broadcast_create')

        with transaction.atomic():
            bc = Broadcast.objects.create(
                sender=request.user,
                subject=subject,
                body=body,
                target_role=target_role
            )

            if target_role == 'all':
                recipients_qs = CustomUser.objects.exclude(id=request.user.id)
            elif target_role in ('jobseeker','employer'):
                recipients_qs = CustomUser.objects.filter(user_type=target_role)
            elif target_role == 'specific':
                recipients_qs = CustomUser.objects.filter(id__in=specific_ids)
            else:
                recipients_qs = CustomUser.objects.none()

            if target_role == 'specific':
                bc.recipients.set(recipients_qs)

            now = timezone.now()
            messages_bulk = []
            notifications_bulk = []
            for user in recipients_qs.iterator():
                messages_bulk.append(Message(
                    sender=request.user,
                    recipient=user,
                    subject=subject,
                    body=body,
                    sent_at=now,
                    is_broadcast=True
                ))
                notifications_bulk.append(Notification(
                    user=user,
                    title=subject,
                    message=(body[:250] + '...') if len(body) > 250 else body,
                    link=reverse('communications:inbox'),
                    created_at=now,
                    target_role=target_role
                ))

            if messages_bulk:
                Message.objects.bulk_create(messages_bulk, batch_size=1000)
            if notifications_bulk:
                Notification.objects.bulk_create(notifications_bulk, batch_size=1000)

        dj_messages.success(request, f"Broadcast sent to {recipients_qs.count()} users.")
        return redirect('communications:broadcast_create')

    users = CustomUser.objects.exclude(id=request.user.id).order_by('username')[:500]
    return render(request, 'communications/broadcast_form.html', {'users': users})

@login_required
def delete_notification(request, notification_id):
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    note.delete()
    messages.success(request, "Notification deleted successfully.")
    return redirect('communications:notification_list')

@login_required
def mark_as_read(request, notification_id):
    """Mark a notification as read."""
    
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    note.is_read = True
    note.save()
    messages.success(request, "Notification marked as read.")
    return redirect('communications:notification_list')