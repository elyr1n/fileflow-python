import stripe

from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import SubscriptionPlan, UserSubscription
from accounts.models import CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def subscription_plans(request):
    try:
        subscription = UserSubscription.objects.get(
            user=request.user, is_active=True, end_date__gte=timezone.now()
        )
        has_active_subscription = True
        days_remaining = (subscription.end_date - timezone.now()).days
    except UserSubscription.DoesNotExist:
        has_active_subscription = False
        days_remaining = 0
        subscription = None

    if not has_active_subscription and request.user.plan == "premium":
        has_active_subscription = True
        days_remaining = 30

    is_superuser = request.user.is_superuser
    if is_superuser:
        user_plan_display = "Премиум"
        days_remaining = "∞"
        superuser_message = (
            "Вы являетесь суперпользователем. Для вас подписка бесконечна!"
        )
    else:
        user_plan_display = "Премиум" if has_active_subscription else "Нет подписки"
        superuser_message = ""

    plans = SubscriptionPlan.objects.filter(is_active=True)

    return render(
        request,
        "payment/subscription_plans.html",
        {
            "has_subscription": has_active_subscription or is_superuser,
            "user_plan": user_plan_display,
            "subscription": subscription,
            "days_remaining": days_remaining,
            "is_superuser": is_superuser,
            "superuser_message": superuser_message,
            "plans": plans,
        },
    )


@login_required
def create_checkout_session(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    try:
        active_subscription = UserSubscription.objects.get(
            user=request.user, is_active=True, end_date__gte=timezone.now()
        )
        messages.warning(request, "У вас уже есть активная подписка!")
        return redirect("payment:subscription_plans")
    except UserSubscription.DoesNotExist:
        pass

    try:
        success_url = (
            request.build_absolute_uri(reverse("payment:success"))
            + "?session_id={CHECKOUT_SESSION_ID}"
        )
        cancel_url = request.build_absolute_uri(reverse("payment:cancel"))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": plan.name},
                        "unit_amount": int(plan.price * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": request.user.id, "plan_id": plan.id},
        )

        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect("payment:subscription_plans")


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")

    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                user_id = session.metadata.get("user_id")
                plan_id = session.metadata.get("plan_id")

                user = CustomUser.objects.get(id=user_id)
                plan = SubscriptionPlan.objects.get(id=plan_id)

                subscription = UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    status="active",
                    is_active=True,
                    end_date=timezone.now()
                    + timezone.timedelta(days=plan.duration_days),
                )

                user.plan = "premium"
                user.save()

                messages.success(request, "Подписка успешно активирована!")

        except Exception as e:
            messages.error(request, f"Ошибка активации подписки: {e}")

    return render(request, "payment/success.html")


@login_required
def payment_cancel(request):
    return render(request, "payment/cancel.html")


@login_required
def subscription_status(request):
    try:
        subscription = UserSubscription.objects.get(
            user=request.user, is_active=True, end_date__gte=timezone.now()
        )
        has_active_subscription = True
    except UserSubscription.DoesNotExist:
        has_active_subscription = False
        subscription = None

    if not has_active_subscription and request.user.plan == "premium":
        has_active_subscription = True

    is_superuser = request.user.is_superuser
    if is_superuser:
        user_plan_display = "Премиум"
    else:
        user_plan_display = "Премиум" if has_active_subscription else "Нет подписки"

    return render(
        request,
        "payment/subscription_status.html",
        {
            "has_subscription": has_active_subscription or is_superuser,
            "user_plan": user_plan_display,
            "subscription": subscription,
        },
    )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    return HttpResponse(status=200)
