from django.urls import path

from . import views

app_name = "hotel"

urlpatterns = [
    path("", views.home, name="home"),
    path("suites/", views.suite_list, name="suite_list"),
    path("suites/<slug:slug>/", views.suite_detail, name="suite_detail"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
]
