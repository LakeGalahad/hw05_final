import datetime as dt
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        get_user_model().objects.create(username="test")
        for i in range(13):
            Post.objects.create(
                text="test"+str(i),
                pub_date=dt.date.today(),
                author=get_user_model().objects.first(),
                group=None
            )

    def setUp(self) -> None:
        cache.clear()
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
