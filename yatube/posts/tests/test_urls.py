from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='тестовый текст тестовой записи',
            author=cls.user,
            group=cls.group
        )
        cls.page_not_found = '/some-non-existing-page/'
        cls.not_author_user = User.objects.create_user(username='notAuthor')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author_user)

    def test_guest_user_pages(self):
        pages = [
            '/',
            f'/{self.user.username}/',
            f'/{self.user.username}/{self.post.pk}/',
            '/groups/',
            f'/group/{self.group.slug}/'
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_pages(self):
        pages = [
            '/new/',
            f'/{self.user.username}/{self.post.pk}/edit/',
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect(self):
        pages = {
            '/new/': f'{reverse("login")}?next=/new/',
            f'/{self.user.username}/{self.post.pk}/edit/':
                f'{reverse("login")}'
                f'?next=/{self.user.username}/{self.post.pk}/edit/',
            f'/{self.user.username}/{self.post.pk}/comment/':
                f'{reverse("login")}'
                f'?next=/{self.user.username}/{self.post.pk}/comment/'
        }
        for page, redirect_page in pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, redirect_page)

    def test_redirect_not_author_edit(self):
        response = self.not_author_client.get(
            f'/{self.user.username}/{self.post.pk}/edit/',
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            f'/{self.user.username}/{self.post.pk}/'
        )

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'index.html',
            f'/{self.user.username}/': 'profile.html',
            f'/{self.user.username}/{self.post.pk}/': 'post.html',
            f'/{self.user.username}/{self.post.pk}/edit/': 'new_post.html',
            '/new/': 'new_post.html',
            '/groups/': 'groups.html',
            f'/group/{self.group.slug}/': 'group.html',

        }
        for page, template in templates_url_names.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        response = self.guest_client.get(self.page_not_found)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'misc/404.html')
