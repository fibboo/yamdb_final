import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post
from yatube import settings

User = get_user_model()

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug-2',
            description='Тестовое описание группы 2'
        )
        cls.post = Post.objects.create(
            text='тестовый текст тестовой записи',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_create_post(self):
        image_for_new_post = SimpleUploadedFile(
            name='test_image_new.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        image_new_address = 'posts/test_image_new.gif'
        new_text = 'M-test'
        posts_count = Post.objects.count()
        form_fields = {
            'group': self.group.pk,
            'text': new_text,
            'image': image_for_new_post
        }

        response = self.authorized_client.post(
            reverse('new_post'),
            form_fields,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        new_post = Post.objects.filter(
            text=new_text,
            group=self.group,
            image=image_new_address,
            author=self.user,
        ).exists()
        self.assertTrue(new_post)

    def test_edit_post(self):
        image_for_edit_post = SimpleUploadedFile(
            name='test_image_edit.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        image_edit_address = 'posts/test_image_edit.gif'
        edit_text = 'измененный тестовый текст'
        posts_count = Post.objects.count()
        form_fields = {
            'group': self.group2.pk,
            'text': edit_text,
            'image': image_for_edit_post
        }

        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            ),
            form_fields,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        edited_post = Post.objects.filter(
            text=edit_text,
            group=self.group2,
            image=image_edit_address,
            author=self.user,
            pk=self.post.pk
        ).exists()
        self.assertTrue(edited_post)
