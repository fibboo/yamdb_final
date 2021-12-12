import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Review, Title

User = get_user_model()


class Command(BaseCommand):
    help = 'Read csv and write data to db'

    def handle(self, *args, **options):
        with open(
                'static/data/review.csv', encoding='utf-8', newline=''
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                pk = row.get('id')

                title_id = Title.objects.get(pk=row.get('title_id'))
                text = row.get('text')
                author = User.objects.get(pk=row.get('author'))
                score = row.get('score')
                pub_date = row.get('pub_date')

                Review.objects.create(
                    id=pk, title_id=title_id, text=text, author=author,
                    score=score, pub_date=pub_date,
                )

        with open(
                'static/data/comment.csv', encoding='utf-8', newline=''
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                pk = row.get('id')
                review_id = Review.objects.get(pk=row.get('review_id'))
                text = row.get('text')
                author = User.objects.get(pk=row.get('author'))
                pub_date = row.get('pub_date')

                Review.objects.create(
                    pk=pk, review_id=review_id, text=text,
                    author=author, pub_date=pub_date,
                )
