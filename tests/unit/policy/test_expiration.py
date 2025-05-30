import re
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from requests_cache.policy.expiration import (
    DO_NOT_CACHE,
    EXPIRE_IMMEDIATELY,
    get_expiration_datetime,
    get_url_expiration,
    utcnow,
)
from requests_cache.policy.directives import set_request_headers
from tests.conftest import HTTPDATE_DATETIME, HTTPDATE_STR


@patch('requests_cache.expiration.datetime')
def test_get_expiration_datetime__no_expiration(mock_datetime):
    assert get_expiration_datetime(None) is None
    assert get_expiration_datetime(-1) is None
    assert get_expiration_datetime(EXPIRE_IMMEDIATELY) == mock_datetime.now(timezone.utc)
    # test 'Expires: 0' (str)
    assert get_expiration_datetime('0') is mock_datetime.now(timezone.utc)
    # test 'Expires: -1' (str) - Azure silliness
    assert get_expiration_datetime('-1') is mock_datetime.now(timezone.utc)


@pytest.mark.parametrize(
    'expire_after, expected_expiration_delta',
    [
        (timedelta(seconds=60), timedelta(seconds=60)),
        (60, timedelta(seconds=60)),
        (33.3, timedelta(seconds=33.3)),
    ],
)
def test_get_expiration_datetime__relative(expire_after, expected_expiration_delta):
    expires = get_expiration_datetime(expire_after)
    expected_expiration = utcnow() + expected_expiration_delta
    # Instead of mocking datetime (which adds some complications), check for approximate value
    assert abs((expires - expected_expiration).total_seconds()) <= 1


def test_get_expiration_datetime__tzinfo():
    tz = timezone(-timedelta(hours=5))
    dt = datetime(2021, 2, 1, 7, 0, tzinfo=tz)
    assert get_expiration_datetime(dt) == datetime(2021, 2, 1, 12, 0, tzinfo=timezone.utc)


def test_get_expiration_datetime__httpdate():
    assert get_expiration_datetime(HTTPDATE_STR) == HTTPDATE_DATETIME
    assert get_expiration_datetime('P12Y34M56DT78H90M12.345S', ignore_invalid_httpdate=True) is None
    with pytest.raises(ValueError):
        get_expiration_datetime('P12Y34M56DT78H90M12.345S')


@pytest.mark.parametrize(
    'url, expected_expire_after',
    [
        ('img.site_1.com', 60 * 60),
        ('http://img.site_1.com/base/img.jpg', 60 * 60),
        ('https://img.site_2.com/base/img.jpg', None),
        ('site_2.com/resource_1', 60 * 60 * 2),
        ('http://site_2.com/resource_1/index.html', 60 * 60 * 2),
        ('http://site_2.com/resource_2/', 60 * 60 * 24),
        ('http://site_2.com/static/', -1),
        ('http://site_2.com/api/resource/123', 60 * 60 * 24 * 7),
        ('http://site_2.com/api/resource/xyz', None),
        ('http://site_2.com/static/img.jpg', -1),
        ('site_2.com', None),
        ('some_other_site.com', None),
        (None, None),
    ],
)
def test_get_url_expiration(url, expected_expire_after, mock_session):
    urls_expire_after = {
        '*.site_1.com': 60 * 60,
        'site_2.com/resource_1': 60 * 60 * 2,
        'site_2.com/resource_2': 60 * 60 * 24,
        re.compile(r'site_2\.com/api/resource/\d+'): 60 * 60 * 24 * 7,
        'site_2.com/static': -1,
    }
    assert get_url_expiration(url, urls_expire_after) == expected_expire_after


@pytest.mark.parametrize(
    'url, expected_expire_after',
    [
        ('https://img.site_1.com/image.jpeg', 60 * 60),
        ('https://img.site_1.com/resource/1', 60 * 60 * 2),
        ('https://site_2.com', 1),
        ('https://any_other_site.com', 1),
    ],
)
def test_get_url_expiration__evaluation_order(url, expected_expire_after):
    """If there are multiple matches, the first match should be used in the order defined"""
    urls_expire_after = {
        '*.site_1.com/resource': 60 * 60 * 2,
        '*.site_1.com': 60 * 60,
        '*': 1,
    }
    assert get_url_expiration(url, urls_expire_after) == expected_expire_after


def test_set_request_headers():
    headers = set_request_headers(
        {'ETag': '123456'},
        expire_after=60,
        only_if_cached=True,
        refresh=True,
        force_refresh=True,
    )
    assert headers['Cache-Control'] == 'max-age=60,must-revalidate,no-cache,only-if-cached'
    assert headers['ETag'] == '123456'


def test_set_request_headers__do_not_cache():
    headers = set_request_headers(
        {},
        expire_after=DO_NOT_CACHE,
        only_if_cached=False,
        refresh=False,
        force_refresh=False,
    )
    assert 'X-ACTUAL-NO-CACHE' in headers
    assert 'Cache-Control' not in headers
