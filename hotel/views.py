from django.shortcuts import get_object_or_404, render

from .models import Suite


def _active_suites():
    return Suite.objects.filter(is_active=True).prefetch_related("photos")


def home(request):
    return render(request, "hotel/home.html", {"suites": _active_suites()[:3]})


def suite_list(request):
    return render(request, "hotel/suite_list.html", {"suites": _active_suites()})


def suite_detail(request, slug):
    suite = get_object_or_404(_active_suites(), slug=slug)
    return render(request, "hotel/suite_detail.html", {"suite": suite})


def about(request):
    return render(request, "hotel/about.html")


def contacts(request):
    return render(request, "hotel/contacts.html")
