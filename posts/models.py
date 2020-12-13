from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
                    verbose_name="Текст поста",
                    help_text="Поделитесь своими мыслями с миром"
                    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey("Group", on_delete=models.SET_NULL,
                              related_name="posts", blank=True,
                              null=True, verbose_name="Название группы",
                              help_text="Выберите группу интересов")
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):

        return self.text[:15]


class Group(models.Model):

    title = models.CharField(max_length=200)
    slug = models.SlugField(null=False, unique=True)
    description = models.TextField()

    def __str__(self):

        return self.title


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(
                    verbose_name="Текст комментария",
                    help_text="Поделитесь своими мыслями с автором"
                    )
    created = models.DateTimeField("date commented", auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
