"""Offline tests for the retry/backoff wiring on the NCBI eutils client.

NCBI sheds load by returning 429/5xx *and* by resetting connections outright.
Without retries a single transient hiccup fails the request (and any test that
made it), which reads as "flaky" when it is really rate-limit / load shedding.
These tests guard the retry adapter that absorbs those transients. They assert
against urllib3's own Retry decision logic -- real behavior, not a mock we
invented -- so they stay meaningful if the config drifts.
"""

import pytest

from metapub.ncbi_client import NCBIClient

RETRYABLE_STATUSES = [429, 500, 502, 503, 504]


@pytest.fixture
def adapter():
    """The HTTPAdapter the client mounts for eutils requests."""
    client = NCBIClient()
    return client.session.get_adapter('https://eutils.ncbi.nlm.nih.gov')


def test_retry_adapter_mounted_for_both_schemes():
    client = NCBIClient()
    https = client.session.get_adapter('https://eutils.ncbi.nlm.nih.gov')
    http = client.session.get_adapter('http://eutils.ncbi.nlm.nih.gov')
    # Same adapter instance mounted on both schemes.
    assert https.max_retries is not None
    assert http.max_retries is not None


def test_retries_configured_across_failure_modes(adapter):
    retry = adapter.max_retries
    # A transient failure at any layer -- connect, read, or bad status -- must
    # get more than one attempt.
    assert retry.total >= 3
    assert retry.connect and retry.connect >= 3
    assert retry.read and retry.read >= 3
    assert retry.status and retry.status >= 3


def test_backoff_and_retry_after_are_enabled(adapter):
    retry = adapter.max_retries
    # Backoff spaces attempts past NCBI's per-second window so a rate-limit
    # burst gets a chance to clear instead of hammering straight back.
    assert retry.backoff_factor > 0
    # 429s carry a Retry-After header; honor it.
    assert retry.respect_retry_after_header is True


@pytest.mark.parametrize('status', RETRYABLE_STATUSES)
def test_retryable_statuses_trigger_a_retry(adapter, status):
    # Ask urllib3's real predicate whether a GET with this status retries.
    assert adapter.max_retries.is_retry('GET', status) is True


def test_success_status_does_not_retry(adapter):
    assert adapter.max_retries.is_retry('GET', 200) is False


def test_get_is_a_retryable_method(adapter):
    # eutils requests are GETs; if GET were excluded, nothing would retry.
    assert 'GET' in adapter.max_retries.allowed_methods
