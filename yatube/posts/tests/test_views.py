import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow, Comment
from yatube import settings

User = get_user_model()

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                text='тестовый текст тестовой записи',
                author=cls.user,
                group=cls.group,
                image=SimpleUploadedFile(
                    name='test_image.gif',
                    content=cls.small_gif,
                    content_type='image/gif'
                )
            )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание группы'
        )
        cls.post_for_group2 = Post.objects.create(
            text='тестовый текст тестовой записи',
            author=cls.user,
            group=cls.group2,
            image=SimpleUploadedFile(
                name='test_image2.gif',
                content=cls.small_gif,
                content_type='image/gif'
            )
        )
        cls.image = SimpleUploadedFile(
            name='test_image3.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.new_text = 'M-test'

    def _post_in_context(self, post):
        post_attrs = {
            post.text: self.post.text,
            post.author: self.user,
            post.group: self.group,
            post.pub_date: self.post.pub_date,
            post.image: self.post.image,
        }
        for value, expected in post_attrs.items():
            return self.assertEqual(value, expected)

    def _group_in_context(self, group):
        group_attrs = {
            group.title: self.group.title,
            group.slug: self.group.slug,
            group.description: self.group.description
        }
        for value, expected in group_attrs.items():
            return self.assertEqual(value, expected)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            reverse('index'): 'index.html',
            (
                reverse('profile', kwargs={'username': self.user.username})
            ): 'profile.html',
            (
                reverse(
                    'post',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.pk
                    }
                )
            ): 'post.html',
            (
                reverse(
                    'post_edit',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.pk
                    }
                )
            ): 'new_post.html',
            reverse('new_post'): 'new_post.html',
            reverse('groups'): 'groups.html',
            reverse('group', kwargs={'slug': self.group.slug}): 'group.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        post = response.context['page'][0]
        self._post_in_context(post)

    def test_group_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'group', kwargs={'slug': self.group.slug}
        ))
        post = response.context['page'][0]
        self._post_in_context(post)

        group = response.context['group']
        self._group_in_context(group)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'profile', kwargs={'username': self.user.username}
        ))
        post = response.context['page'][0]
        self._post_in_context(post)

        author = response.context['author']
        self.assertEqual(author, self.user)

    def test_groups_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('groups'))
        group = response.context['groups'][0]
        self._group_in_context(group)

    def test_new_post_page_shows_correct_context(self):
        response_new = self.authorized_client.get(reverse('new_post'))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_new.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        nav_bar_context = response_new.context['nav_bar']
        is_new_context = response_new.context['new']
        self.assertEqual(nav_bar_context, 'new_post')
        self.assertEqual(is_new_context, True)

    def test_edit_post_page_shows_correct_context(self):
        response_edit = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_edit.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.pk
                }
            )
        )
        post = response.context['post']
        self._post_in_context(post)

    def test_new_post_appears_on_index_page(self):
        new_post = Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.user,
            image=self.image
        )

        response_index = self.guest_client.get(reverse('index'))
        index_posts_list = response_index.context.get('page').object_list
        self.assertIn(new_post, index_posts_list)

    def test_new_post_appears_on_group_page(self):
        new_post = Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.user,
            image=self.image
        )

        response_post_group = self.guest_client.get(reverse(
            'group', kwargs={'slug': self.group.slug}
        ))
        group_posts_list = response_post_group.context.get('page').object_list
        self.assertIn(new_post, group_posts_list)

    def test_new_post_dont_appears_other_group_page(self):
        new_post = Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.user,
            image=self.image
        )

        response_non_post_group = self.guest_client.get(reverse(
            'group', kwargs={'slug': self.group2.slug}
        ))
        non_group_posts_list = \
            response_non_post_group.context.get('page').object_list
        self.assertNotIn(new_post, non_group_posts_list)

    def test_first_page(self):
        views = [
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username})
        ]

        for view in views:
            with self.subTest(view=view):
                response = self.guest_client.get(view)
                object_list = response.context.get('page').object_list
                self.assertEqual(len(object_list), 10)

    def test_second_index_page_contains_three_records(self):
        view = reverse('group', kwargs={'slug': self.group.slug})

        response = self.guest_client.get(view + '?page=2')
        object_list = response.context.get('page').object_list
        self.assertEqual(len(object_list), 3)

    def test_second_group_page_contains_three_records(self):
        view = reverse('group', kwargs={'slug': self.group.slug})

        response = self.guest_client.get(view + '?page=2')
        object_list = response.context.get('page').object_list
        self.assertEqual(len(object_list), 3)


class CacheTest(TestCase):
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
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.new_text = 'M-test'

    def test_index_page_cache(self):
        response_before = self.guest_client.get(reverse('index'))
        Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.user,
        )
        response_after = self.guest_client.get(reverse('index'))

        self.assertEqual(response_before.content, response_after.content)
        self.assertTrue(response_after.context is None)

    def test_group_page_cache(self):
        response_before = self.guest_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.user
        )
        response_after = self.guest_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )

        self.assertEqual(response_before.content, response_after.content)
        self.assertTrue(response_after.context is None)


class SubscribeTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='JustUser')
        cls.following = 1

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.new_text = 'new post text'
        cls.following_count_after_unfollow = 0
        cls.post = Post.objects.create(
            text='тестовый текст тестовой записи',
            author=cls.author,
            group=cls.group,
        )
        cls.test_comment_text = 'test comment'

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_auth_user_can_subscribe(self):
        following_before_exists = Follow.objects.filter(
            user=self.user,
            author=self.author
        ).all().exists()

        self.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': self.author.username},
        ))

        following_after = Follow.objects.filter(
            user=self.user,
            author=self.author
        ).all()

        self.assertNotEqual(following_before_exists, following_after.exists())
        self.assertEqual(following_after.count(), self.following)

    def test_auth_user_can_unsubscribe(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        following_before_exists = Follow.objects.filter(
            user=self.user,
            author=self.author
        ).all().exists()

        self.authorized_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.author.username}
        ))

        after_unfollow = Follow.objects.filter(
            user=self.user,
            author=self.author
        ).all()

        self.assertNotEqual(following_before_exists, after_unfollow.exists())
        self.assertEqual(after_unfollow.count(),
                         self.following_count_after_unfollow)

    def test_new_post_appears_follower_page(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )

        new_post = Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.author,
        )

        response = self.authorized_client.get(reverse('follow_index'))
        posts_list = response.context.get('page').object_list
        self.assertIn(new_post, posts_list)

    def test_new_post_dont_appears_other_group_page(self):
        Follow.objects.create(
            user=self.user,
            author=self.author
        )

        new_post = Post.objects.create(
            group=self.group,
            text=self.new_text,
            author=self.user,
        )

        response = self.authorized_client.get(reverse('follow_index'))
        posts_list = response.context.get('page').object_list
        self.assertNotIn(new_post, posts_list)

    def test_cant_subscribe_self(self):
        self.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': self.user.username}
        ))

        following_exists = Follow.objects.filter(
            user=self.user,
            author=self.user,
        ).exists()

        self.assertFalse(following_exists)

    def test_subscribe_only_once(self):
        following_count_before = 1
        self.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': self.user.username}
        ))
        self.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': self.user.username}
        ))

        following_count = Follow.objects.filter(
            user=self.user,
            author=self.user,
        ).count()

        self.assertNotEqual(following_count, following_count_before)

    def test_auth_user_can_comment_post(self):
        comment_exists_before = Comment.objects.filter(
            author=self.user,
            post=self.post
        ).all().exists()

        self.authorized_client.post(
            reverse(
                'add_comment',
                kwargs={'username': self.author.username,
                        'post_id': self.post.pk}
            ),
            {'text': self.test_comment_text},
            follow=True
        )

        comment_exists_after = Comment.objects.filter(
            author=self.user,
            post=self.post,
            text=self.test_comment_text
        ).exists()

        self.assertNotEqual(comment_exists_before, comment_exists_after)
        self.assertTrue(comment_exists_after)

    def test_guest_user_cant_comment_post(self):
        comment_exists_before = Comment.objects.filter(
            author=self.user,
            post=self.post
        ).all().exists()

        self.guest_client.post(
            reverse(
                'add_comment',
                kwargs={'username': self.author.username,
                        'post_id': self.post.pk}
            ),
            {'text': self.test_comment_text},
            follow=True
        )

        comment_exists_after = Comment.objects.filter(
            author=self.user,
            post=self.post,
            text=self.test_comment_text
        ).all().exists()

        self.assertEqual(comment_exists_before, comment_exists_after)
        self.assertFalse(comment_exists_after)
