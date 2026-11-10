"""Tests for SIMBAD mirror selection (mocked, so no network is needed)."""

import pytest
import requests
from astroquery.simbad import conf as simbad_conf

import astrodb_utils.sources as sources
import astrodb_utils.utils as utils
from astrodb_utils import AstroDBError
from astrodb_utils.sources import find_source_in_db, find_survey_name_in_simbad
from astrodb_utils.utils import select_simbad_mirror, set_simbad_mirror, simbad_available


class FakeResponse:
    def __init__(self, ok):
        self.ok = ok


@pytest.fixture(autouse=True)
def restore_simbad_state():
    """Undo any mirror changes so other tests are unaffected."""
    old_server = utils.Simbad.server
    old_servers = list(simbad_conf.servers_list)
    old_status = utils._simbad_status
    yield
    utils._simbad_status = old_status
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


def test_simbad_available_caches_and_rechecks(monkeypatch):
    calls = []

    def fake_select():  # behaves like select_simbad_mirror when every mirror is down
        calls.append(1)
        utils._simbad_status = (None, utils.time.monotonic())

    monkeypatch.setattr(utils, "select_simbad_mirror", fake_select)
    utils._simbad_status = None
    assert simbad_available() is False
    assert simbad_available() is False  # remembered, no second probe
    assert len(calls) == 1
    monkeypatch.setattr(utils, "SIMBAD_RECHECK_SECONDS", -1)  # failure memory expired
    simbad_available()
    assert len(calls) == 2


def test_simbad_available_remembers_success(monkeypatch):
    monkeypatch.setattr(utils.requests, "get", fake_get(["simbad.harvard.edu"]))
    utils._simbad_status = None
    assert simbad_available() is True
    monkeypatch.setattr(utils.requests, "get", fake_get([]))  # now everything is down...
    assert simbad_available() is True  # ...but the earlier success is remembered


def test_find_source_ignores_simbad_when_down(db, monkeypatch):
    monkeypatch.setattr(sources, "simbad_available", lambda: False)

    def fail(*args, **kwargs):
        raise AssertionError("SIMBAD should not be queried")

    monkeypatch.setattr(sources.Simbad, "query_object", fail)
    assert find_source_in_db(db, "Some Unknown Source XYZ") == []


def test_find_survey_name_raises_when_simbad_down(monkeypatch):
    monkeypatch.setattr(sources, "simbad_available", lambda: False)
    with pytest.raises(AstroDBError, match="SIMBAD is not reachable"):
        find_survey_name_in_simbad({"source": ["Gl 229"]}, "Gaia DR2")
