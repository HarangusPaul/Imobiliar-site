from django.test import RequestFactory

from core.logging import REQUEST_ID_HEADER, get_request_id
from core.middleware import RequestIDMiddleware


def test_request_id_is_generated_and_echoed():
    seen = {}

    def view(request):
        seen["inside"] = get_request_id()
        from django.http import HttpResponse

        return HttpResponse("ok")

    response = RequestIDMiddleware(view)(RequestFactory().get("/"))
    assert response[REQUEST_ID_HEADER] == seen["inside"]
    assert get_request_id() == ""  # contextvar is reset after the request


def test_client_supplied_request_id_is_honoured_but_truncated():
    from django.http import HttpResponse

    middleware = RequestIDMiddleware(lambda request: HttpResponse("ok"))
    request = RequestFactory().get("/", headers={"x-request-id": "a" * 200})
    assert len(middleware(request)[REQUEST_ID_HEADER]) == 64
