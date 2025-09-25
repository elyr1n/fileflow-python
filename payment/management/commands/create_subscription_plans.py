from django.core.management.base import BaseCommand
import stripe
from django.conf import settings
from payment.models import SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = "Create subscription plans in Stripe and database"

    def handle(self, *args, **options):
        plan, created = SubscriptionPlan.objects.get_or_create(
            name="Basic Subscription",
            defaults={
                "description": "Доступ к премиум-функциям загрузки файлов на 30 дней.",
                "price": 5.00,
                "duration_days": 30,
            },
        )

        if created or not plan.stripe_price_id:
            try:
                product = stripe.Product.create(
                    name=plan.name,
                    description=plan.description,
                )

                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(plan.price * 100),
                    currency="usd",
                    recurring={"interval": "month"},
                )

                plan.stripe_price_id = price.id
                plan.save()
                self.stdout.write(
                    self.style.SUCCESS("Subscription plan created successfully!")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating plan: {e}"))
