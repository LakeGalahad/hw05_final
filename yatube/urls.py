from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path
from django.conf.urls import handler404, handler500

urlpatterns = [
        path("admin/", admin.site.urls),
        path("auth/", include("users.urls")),
        path("auth/", include("django.contrib.auth.urls")),
]

urlpatterns += [
        path(
                "contacts/",
                views.flatpage,
                {"url": "/contacts/"},
                name="contacts"
        ),
        path("about-us/", views.flatpage, {"url": "/about-us/"}, name="about"),
        path("terms/", views.flatpage, {"url": "/terms/"}, name="terms"),
        path(
                "about-author/",
                views.flatpage,
                {"url": "/about-author/"},
                name="author"
        ),
        path(
                "about-spec/",
                views.flatpage,
                {"url": "/about-spec/"},
                name="spec"
        ),
        path("", include("posts.urls")),
]

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa
