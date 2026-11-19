from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class PrimaryHostMiddleware:
    """Send visitors of an extra domain (for example pushka-hotel.online) to the
    main one, keeping the page they asked for. Off unless PRIMARY_HOST is set."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        primary = settings.PRIMARY_HOST
        if primary:
            host = request.get_host().split(":")[0].lower()
            if host not in (primary, "www." + primary):
                return HttpResponsePermanentRedirect(
                    "%s://%s%s" % (request.scheme, primary, request.get_full_path())
                )
        return self.get_response(request)
