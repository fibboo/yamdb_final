from django.test import Client, TestCase
from django.urls import reverse


class AboutViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            reverse('about:author'): 'about_author.html',
            reverse('about:tech'): 'about_tech.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
