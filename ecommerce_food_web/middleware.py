import os
from django.conf import settings
from django.http import FileResponse, Http404
import re


class MediaServeMiddleware:
    """
    Middleware to serve media files in production environments where DEBUG is False.
    This is typically not recommended for production use, but can be useful for small applications.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Compile the regex pattern for media URLs
        self.media_pattern = re.compile(f"^{settings.MEDIA_URL.lstrip('/')}")

    def __call__(self, request):
        # Continue if this is not a media URL
        if not request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Strip MEDIA_URL from the path to get the relative path
        relative_path = request.path.replace(settings.MEDIA_URL, "", 1)

        # Create the absolute file path
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        # Check if the file exists
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Serve the file directly
            return FileResponse(open(file_path, "rb"))
        else:
            # Return 404 if the file doesn't exist
            raise Http404(f"Media file '{relative_path}' not found")
