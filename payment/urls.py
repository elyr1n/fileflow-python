from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("plans/", views.subscription_plans, name="subscription_plans"),
    path(
        "create-session/<int:plan_id>/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("success/", views.payment_success, name="success"),
    path("cancel/", views.payment_cancel, name="cancel"),
    path("status/", views.subscription_status, name="subscription_status"),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
]
