from .models import HotelInfo


def hotel_info(request):
    return {"hotel": HotelInfo.load()}
