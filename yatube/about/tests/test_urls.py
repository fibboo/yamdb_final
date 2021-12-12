from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_pages_status_200(self):
        pages = [
            '/about/author/',
            '/about/tech/'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/about/author/': 'about_author.html',
            '/about/tech/': 'about_tech.html'
        }
        for page, template in templates_url_names.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertTemplateUsed(response, template)
