from itertools import chain, zip_longest

from django.shortcuts import render

from .models import Suite


def room_photos():
    """Photos of every room shown on the site, mixed together.

    Guests are not promised a particular room, so the page shows the photos
    without names or numbers. They are dealt out like cards: the first photo
    of each room, then the second of each, and so on.
    """
    suites = Suite.objects.filter(is_active=True).prefetch_related("photos")
    rounds = zip_longest(*(suite.photos.all() for suite in suites))
    return [photo for photo in chain.from_iterable(rounds) if photo is not None]


def home(request):
    return render(request, "hotel/home.html", {"photos": room_photos()})
