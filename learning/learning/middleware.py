import time

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date

ADMIN_SESSION_COOKIE_NAME = "admin_sessionid"


class SeparateAdminSessionMiddleware(SessionMiddleware):
    """Keep the Django admin session separate from the public site session.

    The admin lives under ``/admin/`` and uses its own cookie so that logging
    into the admin does not also authenticate you on the public user site
    (and vice versa).
    """

    def _cookie_name(self, request):
        if request.path.startswith("/admin/"):
            return ADMIN_SESSION_COOKIE_NAME
        return settings.SESSION_COOKIE_NAME

    def process_request(self, request):
        session_key = request.COOKIES.get(self._cookie_name(request))
        request.session = self.SessionStore(session_key)

    def process_response(self, request, response):
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response

        cookie_name = self._cookie_name(request)

        need_vary_cookie = False

        # Delete this request's session cookie if the session is empty.
        if cookie_name in request.COOKIES and empty:
            response.delete_cookie(
                cookie_name,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            need_vary_cookie = True
        else:
            need_vary_cookie = accessed
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires = http_date(time.time() + max_age)
                if response.status_code < 500:
                    try:
                        request.session.save()
                    except UpdateError:
                        raise SessionInterrupted(
                            "The request's session was deleted before the request "
                            "completed. The user may have logged out in a concurrent "
                            "request, for example."
                        )
                    response.set_cookie(
                        cookie_name,
                        request.session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=settings.SESSION_COOKIE_SAMESITE,
                    )
                    need_vary_cookie = True

        # NOTE: we intentionally do NOT delete the "other" session cookie here.
        # Admin and the public site use separate cookies (admin_sessionid vs
        # learnsite_sessionid) precisely so that logging into the admin does NOT
        # log the public-site user out, and vice versa. Deleting the sibling
        # cookie here would wipe the public user's session whenever an admin page
        # was loaded.

        # Purge the legacy shared 'sessionid' cookie that was used before the
        # admin/public sessions were split. If a browser still has it, it can
        # hold an old admin session and cause confusing logouts on refresh.
        if "sessionid" in request.COOKIES:
            response.delete_cookie(
                "sessionid",
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )

        if need_vary_cookie:
            patch_vary_headers(response, ("Cookie",))
        return response