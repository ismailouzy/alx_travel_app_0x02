from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing
import random

class Command(BaseCommand):
    help = "Seed the database with sample listing data"

    def handle(self, *args, **kwargs):
        # Create sample users
        for i in range(1, 4):
            username = f"user{i}"
            User.objects.get_or_create(username=username, defaults={'password': 'password'})

        users = User.objects.all()

        # Create listings
        titles = ['Cozy Cabin', 'Urban Loft', 'Beach House']
        locations = ['Denver', 'New York', 'Miami']

        for i in range(3):
            Listing.objects.create(
                title=titles[i],
                description="Sample description",
                location=locations[i],
                price_per_night=random.randint(80, 300),
                host=users[i]
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

