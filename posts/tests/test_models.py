from django.test import TestCase

from posts.models import Group, Post, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        Group.objects.create(
            title="Peck",
            slug="mafia_town",
            description="Revoluton"
        )

        User.objects.create(username="test")

        Post.objects.create(
            text="q"*20,
            author=User.objects.first(),
            group=Group.objects.first()
        )

        cls.post = Post.objects.first()
        cls.group = Group.objects.first()

    def test_verbose_name(self):
        post = PostsModelTest.post
        field_verbose = {
            "text": "Текст поста",
            "group": "Название группы"
        }
        for value, expected in field_verbose.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                    )

    def test_help_text(self):
        post = PostsModelTest.post
        field_verbose = {
            "text": "Поделитесь своими мыслями с миром",
            "group": "Выберите группу интересов"
        }
        for value, expected in field_verbose.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                    )

    def test_post_str(self):
        post = PostsModelTest.post
        text = str(post)
        self.assertEqual(text, "q"*15)

    def test_group_title(self):
        group = PostsModelTest.group
        title = str(group)
        self.assertEqual(title, group.title)
