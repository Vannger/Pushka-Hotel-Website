from django.urls import path

from . import views

app_name = "hotel"

# The whole site is a single page.
urlpatterns = [
    path("", views.home, name="home"),
]
