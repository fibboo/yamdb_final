from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from posts.models import Post, Group, Follow

User = get_user_model()


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')
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

    def test_str_method_post(self):
        post = self.post
        self.assertEqual(str(post), post.text[:15])

    def test_str_method_group(self):
        group = self.group
        self.assertEqual(str(group), group.title)

    def test_user_cant_follow_self(self):
        constraint_name = 'not_following_yourself'
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(user=self.user, author=self.user)
