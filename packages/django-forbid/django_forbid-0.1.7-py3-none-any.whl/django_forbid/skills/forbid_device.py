from device_detector import DeviceDetector
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from . import Access
from . import Settings


class ForbidDeviceMiddleware:
    """Checks if the user device is forbidden."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        device_aliases = {
            "portable media player": "player",
            "smart display": "display",
            "smart speaker": "speaker",
            "feature phone": "phone",
            "car browser": "car",
        }

        devices = Settings.get("DEVICES", [])
        device_type = request.session.get("DEVICE")
        http_ua = request.META.get("HTTP_USER_AGENT")
        verified_ua = request.session.get("VERIFIED_UA", "")

        # Skips if DEVICES empty or user agent is verified.
        if not devices or verified_ua == http_ua:
            return self.get_response(request)

        if not device_type:
            device_detector = DeviceDetector(http_ua)
            device_detector = device_detector.parse()
            device = device_detector.device_type()
            device_type = device_aliases.get(device, device)
            request.session["DEVICE"] = device_type

        if Access(devices).grants(device_type):
            request.session["VERIFIED_UA"] = http_ua
            return self.get_response(request)

        # Erases the user agent from the session.
        request.session["VERIFIED_UA"] = ""

        # Redirects to the FORBIDDEN_DEV URL if set.
        if Settings.has("OPTIONS.URL.FORBIDDEN_DEV"):
            return redirect(Settings.get("OPTIONS.URL.FORBIDDEN_DEV"))

        return HttpResponseForbidden()
