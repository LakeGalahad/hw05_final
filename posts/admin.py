from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description")
    search_fields = ("title",)
    list_filter = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Group, GroupAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "post", "text", "author")
    search_fields = ("author",)
    list_filter = ("author",)
    empty_value_display = "-пусто-"


admin.site.register(Comment, CommentAdmin)
