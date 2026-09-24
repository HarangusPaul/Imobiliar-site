import io

import pytest

from apps.media.models import MediaAsset, MediaCategory
from apps.media.services.attachments import (
    MediaTooLargeError,
    UnsupportedMediaTypeError,
    attach_file,
    detach,
)

pytestmark = pytest.mark.django_db


def _upload(prop, **overrides):
    data = {
        "owner": prop,
        "stream": io.BytesIO(b"fake-image-bytes"),
        "filename": "front.jpg",
        "content_type": "image/jpeg",
        "category": MediaCategory.GALLERY,
        "size_hint": 16,
    }
    data.update(overrides)
    return attach_file(**data)


def test_the_database_stores_a_key_not_the_bytes(make_property):
    asset = _upload(make_property())
    assert asset.file_key
    assert b"fake-image-bytes" not in asset.file_key.encode()
    assert asset.size_bytes == len(b"fake-image-bytes")
    assert asset.checksum


def test_the_first_gallery_image_becomes_the_cover(make_property):
    prop = make_property()
    asset = _upload(prop)
    prop.refresh_from_db()
    assert prop.cover_image_id == asset.pk


def test_a_second_image_does_not_steal_the_cover(make_property):
    prop = make_property()
    first = _upload(prop)
    _upload(prop, filename="kitchen.jpg")
    prop.refresh_from_db()
    assert prop.cover_image_id == first.pk


def test_gallery_order_follows_upload_order(make_property):
    prop = make_property()
    _upload(prop, filename="a.jpg")
    second = _upload(prop, filename="b.jpg")
    assert second.sort_order == 2


def test_unsupported_types_are_rejected(make_property):
    with pytest.raises(UnsupportedMediaTypeError):
        _upload(make_property(), filename="script.exe", content_type="application/x-msdownload")


def test_oversized_files_are_rejected(make_property):
    with pytest.raises(MediaTooLargeError):
        _upload(make_property(), size_hint=50 * 1024 * 1024)


def test_removing_the_cover_promotes_the_next_image(make_property):
    prop = make_property()
    first = _upload(prop, filename="a.jpg")
    second = _upload(prop, filename="b.jpg")

    detach(first)

    prop.refresh_from_db()
    assert prop.cover_image_id == second.pk
    assert MediaAsset.objects.filter(pk=first.pk).count() == 0
    assert MediaAsset.all_objects.filter(pk=first.pk).count() == 1
