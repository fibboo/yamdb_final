import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api_yamdb.settings import BASE_DIR

User = get_user_model()


class Command(BaseCommand):
    help = 'Read static/data/user.csv and write it to db'

    def handle(self, *args, **options):
        with open(os.path.join(BASE_DIR, 'static/data/users.csv')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                user_id = row.get('id')
                username = row.get('username')
                email = row.get('email')
                role = row.get('role')

                User.objects.create_user(
                    username,
                    email,
                    id=user_id,
                    role=role,
                )
