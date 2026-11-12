from django.shortcuts import get_object_or_404, render

from .models import HotelPhoto, Suite


def _active_suites():
    return Suite.objects.filter(is_active=True).prefetch_related("photos")


def home(request):
    # Feature suites that already have photos; keep the suite order otherwise.
    suites = sorted(_active_suites(), key=lambda suite: suite.cover is None)[:3]
    return render(request, "hotel/home.html", {"suites": suites})


def suite_list(request):
    return render(request, "hotel/suite_list.html", {"suites": _active_suites()})


def suite_detail(request, slug):
    suite = get_object_or_404(_active_suites(), slug=slug)
    return render(request, "hotel/suite_detail.html", {"suite": suite})


def about(request):
    return render(request, "hotel/about.html", {"photos": HotelPhoto.objects.all()})


def contacts(request):
    return render(request, "hotel/contacts.html")
