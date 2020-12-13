import datetime as dt
from django.core.cache import cache
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post


class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        user = get_user_model().objects.create(username="test")
        user2 = get_user_model().objects.create(username="test2")
        user3 = get_user_model().objects.create(username="test3")
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
            image=uploaded
        )
        Follow.objects.create(
            user=user,
            author=user3
        )
        Site.objects.create(
            domain='localhost:8000',
            name='localhost:8000'
        )
        FlatPage.objects.create(
            url="/about-author/",
            title="test_author",
            content="test",
        ).sites.add(Site.objects.first())
        FlatPage.objects.create(
            url="/about-spec/",
            title="test_spec",
            content="test",
        ).sites.add(Site.objects.first())
        cls.post = Post.objects.first()
        cls.user = user
        cls.user2 = user2
        cls.user3 = user3
        cls.image = uploaded

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()
        user = ViewsTest.user
        self.user = user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            "index.html": reverse("index"),
            "group.html": reverse("group", kwargs={"slug": "mafia-town"}),
            "new.html": reverse("new_post"),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_context_is_correct(self, url, context_field, kwargs):
        post = Post.objects.first()
        response = self.authorized_client.get(reverse(url, kwargs=kwargs))
        post_text = response.context.get(context_field)[0].text
        post_date = response.context.get(context_field)[0].pub_date
        post_author = response.context.get(context_field)[0].author
        post_group = response.context.get(context_field)[0].group.title
        post_image = response.context.get(context_field)[0].image
        self.assertEqual(post_text, "test")
        self.assertEqual(post_date, post.pub_date)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, "Peck")
        self.assertNotEqual(post_image, None)
        return response

    def test_index_page_show_correct_context(self):
        self.post_context_is_correct("index", "page", {})

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            "group", kwargs={"slug": "mafia-town"}
            ))
        group_title = response.context.get("page")[0].group.title
        group_slug = response.context.get("page")[0].group.slug
        group_description = response.context.get(
            "page"
            )[0].group.description
        self.assertEqual(group_title, "Peck")
        self.assertEqual(group_slug, "mafia-town")
        self.assertEqual(group_description, "Revoluton")

    def test_new_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            "post_edit", kwargs={"username": "test", "post_id": 1}
            ))
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField
        }
        post = response.context.get("post").id
        self.assertEqual(post, 1)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.post_context_is_correct(
            "profile",
            "page",
            {"username": "test"}
        )
        user_request = response.context.get("user").username
        user_profile = response.context.get("user_profile").username
        paginator = len(response.context.get("paginator").object_list)
        self.assertEqual(user_request, "test")
        self.assertEqual(user_profile, self.user.username)
        self.assertEqual(paginator, 1)

    def test_post_page_show_correct_context(self):
        # Часть кода похожа на код в index и profile,
        # но он различается количеством постов, сюда передается только один
        # поэтому я не могу использовать его повторно
        post = ViewsTest.post
        response = self.authorized_client.get(reverse(
            "post", kwargs={"username": "test", "post_id": 1}
            ))
        post_text = response.context.get("post").text
        post_date = response.context.get("post").pub_date
        post_author = response.context.get("post").author
        post_group = response.context.get("post").group.title
        post_image = response.context.get("post").image
        user_request = response.context.get("user").username
        post_id = response.context.get("post_id")
        post_count = response.context.get("post_count")
        user_profile = response.context.get("user_profile").username
        self.assertEqual(post_text, "test")
        self.assertEqual(post_date, post.pub_date)
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_group, "Peck")
        self.assertNotEqual(post_image, None)
        self.assertEqual(user_request, "test")
        self.assertEqual(post_id, 1)
        self.assertEqual(post_count, 1)
        self.assertEqual(user_profile, self.user.username)

    def test_flatpages_show_correct_context(self):
        flatpages = {
            "author": "test_author",
            "spec": "test_spec",
        }
        for reversed_name, expected in flatpages.items():
            with self.subTest(reversed_name=reversed_name):
                response = self.authorized_client.get(reverse(reversed_name))
                flatpage = response.context.get("flatpage").title
                self.assertEqual(flatpage, expected)

    def test_new_post_appears_right(self):
        user = ViewsTest.user
        group = Group.objects.create(
            title="test",
            slug="test-slug",
            description="test"
        )
        Post.objects.create(
            text="test2",
            pub_date=dt.date.today(),
            author=user,
            group=group
        )
        response_index = self.authorized_client.get(reverse("index"))
        post_text_0 = response_index.context.get("page")[0].text
        self.assertEqual(post_text_0, "test2")
        groups_name = {
            "mafia-town": "test",
            "test-slug": "test2"
        }
        for value, expected in groups_name.items():
            with self.subTest(value=value):
                response_group = self.authorized_client.get(reverse(
                    "group", kwargs={"slug": value}
                    ))
                post_text_0 = response_group.context.get("page")[0].text
                self.assertEqual(post_text_0, expected)

    def test_index_cached(self):
        user = ViewsTest.user
        url = reverse("index")
        client = self.authorized_client
        response = client.get(url)
        post_content_before = response.content
        Post.objects.create(
            text="cache",
            pub_date=dt.date.today(),
            author=user,
            group=Group.objects.first(),
            image=None
        )
        response = client.get(url)
        post_content_cached = response.content
        cache.clear()
        response = client.get(url)
        post_content_after = response.content
        self.assertEqual(post_content_before, post_content_cached)
        self.assertNotEqual(post_content_cached, post_content_after)

    def test_authrized_follow(self):
        follow = Follow.objects.count()
        self.authorized_client.get(
            reverse("profile_follow", kwargs={"username": "test2"})
        )
        after_follow = Follow.objects.count()
        self.assertEqual(after_follow, follow + 1)

    def test_authrized_unfollow(self):
        follow = Follow.objects.count()
        self.authorized_client.get(
            reverse("profile_unfollow", kwargs={"username": "test3"})
        )
        after_follow = Follow.objects.count()
        self.assertEqual(after_follow, follow - 1)

    def test_only_followers_see_post(self):
        user = ViewsTest.user3
        user2 = ViewsTest.user2
        Post.objects.create(
            text="test3",
            pub_date=dt.date.today(),
            author=user,
            group=Group.objects.first()
        )
        response1 = self.authorized_client.get(reverse("follow_index"))
        self.authorized_client.force_login(user2)
        response2 = self.authorized_client.get(reverse("follow_index"))
        self.assertNotEqual(response1.content, response2.content)

    def test_authorized_comments_only(self):
        comments = Comment.objects.filter(post=Post.objects.first()).count()
        comment = {
            "text": "test"
        }
        self.authorized_client.post(
            reverse("add_comment", kwargs={
                "username": "test",
                "post_id": Post.objects.first().pk
            }),
            data=comment,
        )
        comments_new_authorized = Comment.objects.filter(
            post=Post.objects.first()
        ).count()
        self.assertEqual(comments_new_authorized, comments + 1)
        self.guest_client.post(
            reverse("add_comment", kwargs={
                "username": "test",
                "post_id": Post.objects.first().pk
            }),
            data=comment,
        )
        comments_new_guest = Comment.objects.filter(
            post=Post.objects.first()
        ).count()
        self.assertEqual(comments_new_guest, comments_new_authorized)
