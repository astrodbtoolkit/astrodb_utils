"""Tests for SIMBAD mirror selection (mocked, so no network is needed)."""

import pytest
import requests
from astroquery.simbad import conf as simbad_conf

import astrodb_utils.utils as utils
from astrodb_utils.utils import select_simbad_mirror, set_simbad_mirror


class FakeResponse:
    def __init__(self, ok):
        self.ok = ok


@pytest.fixture(autouse=True)
def restore_simbad_state():
    """Undo any mirror changes so other tests are unaffected."""
    old_server = utils.Simbad.server
    old_servers = list(simbad_conf.servers_list)
    yield
    simbad_conf.servers_list = old_servers
    utils.Simbad.server = old_server


def fake_get(up_hosts, not_ok_hosts=()):
    """Mock for requests.get: listed hosts respond, `not_ok_hosts` return an error status, others time out."""

    def _get(url, timeout=None):
        if any(host in url for host in up_hosts):
            return FakeResponse(True)
        if any(host in url for host in not_ok_hosts):
            return FakeResponse(False)
        raise requests.exceptions.ConnectTimeout

    return _get


def test_select_mirror_prefers_first(monkeypatch):
    monkeypatch.setattr(utils.requests, "get", fake_get(["simbad.cds.unistra.fr", "simbad.harvard.edu"]))
    assert select_simbad_mirror() == "simbad.cds.unistra.fr"
    assert utils.Simbad.server == "simbad.cds.unistra.fr"


def test_select_mirror_falls_back_after_error_status_and_timeout(monkeypatch):
    # Strasbourg answers with an error (like the 404 seen during the incident), Harvard times out
    monkeypatch.setattr(
        utils.requests, "get", fake_get(["simbad.idia.ac.za"], not_ok_hosts=["simbad.cds.unistra.fr"])
    )
    assert select_simbad_mirror() == "simbad.idia.ac.za"
    assert utils.Simbad.server == "simbad.idia.ac.za"


def test_select_mirror_none_available(monkeypatch):
    monkeypatch.setattr(utils.requests, "get", fake_get([]))
    utils.Simbad.server = "simbad.harvard.edu"
    assert select_simbad_mirror() is None
    assert utils.Simbad.server == "simbad.harvard.edu"  # unchanged


def test_set_mirror_cleans_host_and_registers_unknown_servers():
    set_simbad_mirror("https://simbad.idia.ac.za/")
    assert utils.Simbad.server == "simbad.idia.ac.za"
    assert "simbad.idia.ac.za" in simbad_conf.servers_list
