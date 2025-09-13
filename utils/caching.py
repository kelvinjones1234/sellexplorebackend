import zlib
from django.http import HttpResponseNotModified
from django.utils.http import parse_http_date_safe, http_date
from django.db.models import Max


class CacheHeadersMixin:
    """
    DRF-aware caching mixin that adds ETag and Last-Modified headers.

    Usage:
    1. Inherit this mixin in your View.
    2. In your `get` method, retrieve your object or queryset.
    3. Set `self.object = ...` or `self.queryset = ...` (can be a single queryset or a tuple of querysets).
    4. Call `not_modified = self.check_not_modified(request)` at the beginning.
    5. If `not_modified`, return it immediately to short-circuit the view.

    The mixin's `finalize_response` will automatically add the correct
    cache headers to successful (200 OK) responses.
    """

    cache_control = "public, max-age=0, must-revalidate"

    def get_last_modified(self, target):
        """Return the latest modified timestamp for an object, queryset, or tuple of querysets."""
        if not target:
            return None

        if isinstance(target, tuple):  # Handle tuple of querysets
            last_modified = None
            for qs in target:
                if hasattr(qs, "all"):  # It's a queryset
                    qs_last_modified = qs.aggregate(last_modified=Max("updated_at"))[
                        "last_modified"
                    ]
                    if qs_last_modified and (
                        last_modified is None or qs_last_modified > last_modified
                    ):
                        last_modified = qs_last_modified
            return last_modified
        elif hasattr(target, "all"):  # It's a queryset
            return target.aggregate(last_modified=Max("updated_at"))["last_modified"]
        elif hasattr(target, "updated_at"):  # It's a model instance
            return target.updated_at
        return None

    def get_etag(self, target):
        """Generate a weak ETag using CRC32 for an object, queryset, or tuple of querysets."""
        if not target:
            return None

        last_modified = self.get_last_modified(target)
        if not last_modified:
            return None

        timestamp = int(last_modified.timestamp())

        if isinstance(target, tuple):  # Handle tuple of querysets
            etag_strings = []
            for qs in target:
                if hasattr(qs, "all"):  # Queryset
                    try:
                        count = qs.count()
                        model_name = qs.model.__name__.lower()
                        etag_strings.append(f"{model_name}-set-{timestamp}-{count}")
                    except Exception:
                        model_name = qs.model.__name__.lower()
                        etag_strings.append(f"{model_name}-set-{timestamp}")
            # Combine all etag strings into one
            combined_etag = ":".join(sorted(etag_strings))
            etag_crc = zlib.crc32(combined_etag.encode())
            return f'W/"{etag_crc:x}"'

        if hasattr(target, "all"):  # Queryset
            try:
                count = target.count()
                model_name = target.model.__name__.lower()
                etag_string = f"{model_name}-set-{timestamp}-{count}"
                etag_crc = zlib.crc32(etag_string.encode())
                return f'W/"{etag_crc:x}"'
            except Exception:
                model_name = target.model.__name__.lower()
                return f'W/"{model_name}-set-{timestamp}"'

        # Model instance
        pk = getattr(target, "pk", "no-pk")
        etag_string = f"{pk}-{timestamp}"
        etag_crc = zlib.crc32(etag_string.encode())
        return f'W/"{etag_crc:x}"'

    def check_not_modified(self, request):
        """
        Checks request headers against the target's ETag/Last-Modified.
        Returns HttpResponseNotModified if the client's cache is still valid, else None.
        """
        target = getattr(self, "object", None) or getattr(self, "queryset", None)
        if target is None:
            return None

        etag = self.get_etag(target)
        last_modified = self.get_last_modified(target)

        # ETag check
        if_none_match = request.headers.get("If-None-Match")
        if if_none_match and etag:
            client_etags = [tag.strip() for tag in if_none_match.split(",")]
            if etag in client_etags or "*" in client_etags:
                response = HttpResponseNotModified()
                response["ETag"] = etag
                if last_modified:
                    response["Last-Modified"] = http_date(last_modified.timestamp())
                response["Cache-Control"] = self.cache_control
                return response

        # Last-Modified check
        if_modified_since = request.headers.get("If-Modified-Since")
        if request.method == "GET" and if_modified_since and last_modified:
            try:
                client_time = parse_http_date_safe(if_modified_since)
                server_time = int(last_modified.timestamp())
                if client_time and client_time >= server_time:
                    response = HttpResponseNotModified()
                    if etag:
                        response["ETag"] = etag
                    response["Last-Modified"] = http_date(last_modified.timestamp())
                    response["Cache-Control"] = self.cache_control
                    return response
            except (ValueError, TypeError):
                pass

        return None

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Sets caching headers on the outgoing response if it's a 200 OK.
        """
        final_response = super().finalize_response(request, response, *args, **kwargs)

        target = getattr(self, "object", None) or getattr(self, "queryset", None)
        if (
            request.method == "GET"
            and target is not None
            and final_response.status_code == 200
        ):
            etag = self.get_etag(target)
            last_modified = self.get_last_modified(target)

            if etag:
                final_response["ETag"] = etag
            if last_modified:
                final_response["Last-Modified"] = http_date(last_modified.timestamp())

            final_response["Cache-Control"] = self.cache_control

            # Optional Vary support
            vary_headers = []
            if hasattr(self, "vary_headers"):
                vary_headers.extend(self.vary_headers)
            if vary_headers:
                final_response["Vary"] = ", ".join(vary_headers)

        return final_response