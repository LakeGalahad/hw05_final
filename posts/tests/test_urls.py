import datetime as dt
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        user1 = get_user_model().objects.create(username="test")
        user2 = get_user_model().objects.create(username="test2")
        Group.objects.create(
            title="Peck",
            slug="mafia-town",
            description="Revoluton"
        )
        Post.objects.create(
            text="test",
            pub_date=dt.date.today(),
            author=user1,
            group=Group.objects.first()
        )
        Site.objects.create(
            domain='localhost:8000',
            name='localhost:8000'
        )
        FlatPage.objects.create(
            url="/about-author/",
            title="test_author",
        ).sites.add(Site.objects.first())
        FlatPage.objects.create(
            url="/about-spec/",
            title="test_spec",
        ).sites.add(Site.objects.first())

        cls.user1 = user1
        cls.user2 = user2

    def setUp(self) -> None:
        cache.clear()
        user1 = URLTests.user1
        self.guest_client = Client()
        self.user = user1
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_exists(self):
        page_exists = [
            reverse("index"),
            reverse("group", kwargs={"slug": "mafia-town"}),
            reverse("profile", kwargs={"username": "test"}),
            reverse("post", kwargs={"username": "test", "post_id": 1}),
            reverse("author"),
            reverse("spec"),
        ]
        for page in page_exists:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_authorized(self):
        page_auth = [
            reverse("new_post"),
            reverse("post_edit", kwargs={"username": "test", "post_id": 1}),
        ]
        for page in page_auth:
            with self.subTest():
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_redirect_anonymus(self):
        page_auth = {
            reverse("new_post"):
            reverse("login") + "?next="+reverse("new_post"),
            reverse("post_edit", kwargs={
                "username": "test",
                "post_id": 1
            }): reverse("login")+"?next=" + reverse("post_edit", kwargs={
                "username": "test",
                "post_id": 1
            }),
        }
        for page, expected in page_auth.items():
            with self.subTest(expected=expected):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, expected)

    def test_redirect_authorized(self):
        user2 = URLTests.user2
        self.user = user2
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            reverse("post_edit", kwargs={
                "username": "test",
                "post_id": 1
            }),
            follow=True
        )
        self.assertRedirects(response, reverse("post", kwargs={
            "username": "test",
            "post_id": 1
        }))

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            reverse("index"): "index.html",
            reverse("group", kwargs={"slug": "mafia-town"}): "group.html",
            reverse("new_post"): "new.html",
            reverse("post_edit", kwargs={
                "username": "test",
                "post_id": 1
            }): "new.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_404_return(self):
        response = self.guest_client.get(reverse("profile", kwargs={
            "username": "test_404"
        }))
        self.assertEqual(response.status_code, 404)
