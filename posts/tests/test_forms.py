import datetime as dt
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        super().setUpClass()
        user = get_user_model().objects.create(username="test")
        Group.objects.create(
            title="Peck",
            slug="mafia-town",
            description="Revoluton"
        )
        Post.objects.create(
            text="test",
            pub_date=dt.date.today(),
            author=user,
            group=Group.objects.first(),
        )
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.first()
        cls.post = Post.objects.first()
        cls.user = user
        cls.uploaded = uploaded

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        user = PostCreateFormTests.user
        self.user = user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        uploaded = PostCreateFormTests.uploaded
        group = PostCreateFormTests.group
        posts_count = Post.objects.count()
        form_data = {
            "group": group.id,
            "text": "test",
            "image": uploaded
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        group = PostCreateFormTests.group
        form_data = {
            "group": group.id,
            "text": "test_edit",
        }
        response = self.authorized_client.post(
            reverse("post_edit", kwargs={"username": "test", "post_id": 1}),
            data=form_data,
        )
        self.assertRedirects(response, reverse("post", kwargs={
            "username": "test",
            "post_id": 1
        }))
        self.assertEqual(Post.objects.first().text, "test_edit")
