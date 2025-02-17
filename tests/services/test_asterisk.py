# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file
from surrogate import surrogate


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
def test_asterisk_success(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {"login.return_value": 42, "originate.return_value": 42}
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().originate(
                "SIP/avaya/0123456789",
                2222,
                context="default",
                priority="1",
                caller_id=2222,
                variables={"text": "⚽ Notification message ⚽"},
            ),
            call().logoff(),
            call().close(),
        ]

        assert outcome is True
        assert "Authentication 42" in caplog.text
        assert "Call 42" in caplog.text


class ManagerSocketException(Exception):
    pass


class ManagerAuthException(Exception):
    pass


class ManagerException(Exception):
    pass


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch("asterisk.manager.ManagerSocketException", ManagerSocketException, create=True)
def test_asterisk_failure_no_connection(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {"connect.side_effect": ManagerSocketException("something failed")}
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().close(),
        ]

        assert outcome is False
        assert "Error connecting to the manager: something failed" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch("asterisk.manager.ManagerSocketException", ManagerSocketException, create=True)
@mock.patch("asterisk.manager.ManagerAuthException", ManagerAuthException, create=True)
def test_asterisk_failure_login_invalid(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {"login.side_effect": ManagerAuthException("something failed")}
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().close(),
        ]

        assert outcome is False
        assert "Error logging in to the manager: something failed" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch("asterisk.manager.ManagerSocketException", ManagerSocketException, create=True)
@mock.patch("asterisk.manager.ManagerAuthException", ManagerAuthException, create=True)
@mock.patch("asterisk.manager.ManagerException", ManagerException, create=True)
def test_asterisk_failure_originate_croaks(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {
            "login.return_value": 42,
            "originate.side_effect": ManagerException("something failed"),
        }
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().originate(
                "SIP/avaya/0123456789",
                2222,
                context="default",
                priority="1",
                caller_id=2222,
                variables={"text": "⚽ Notification message ⚽"},
            ),
            call().close(),
        ]

        assert outcome is False
        assert "Error: something failed" in caplog.text


@surrogate("asterisk.manager")
@mock.patch("asterisk.manager.Manager", create=True)
@mock.patch("asterisk.manager.ManagerSocketException", ManagerSocketException, create=True)
@mock.patch("asterisk.manager.ManagerAuthException", ManagerAuthException, create=True)
@mock.patch("asterisk.manager.ManagerException", ManagerException, create=True)
def test_asterisk_success_with_broken_close(asterisk_mock, srv, caplog):

    with caplog.at_level(logging.DEBUG):

        attrs = {
            "login.return_value": 42,
            "originate.return_value": 42,
            "close.side_effect": ManagerSocketException("something failed"),
        }
        asterisk_mock.return_value = mock.MagicMock(**attrs)

        module = load_module_from_file("mqttwarn/services/asterisk.py")

        item = Item(
            config={
                "host": "asterisk.example.org",
                "port": 5038,
                "username": "foobar",
                "password": "bazqux",
                "extension": 2222,
                "context": "default",
            },
            target="test",
            addrs=["SIP/avaya/", "0123456789"],
            message="⚽ Notification message ⚽",
        )

        outcome = module.plugin(srv, item)

        assert asterisk_mock.mock_calls == [
            call(),
            call().connect("asterisk.example.org", 5038),
            call().login("foobar", "bazqux"),
            call().originate(
                "SIP/avaya/0123456789",
                2222,
                context="default",
                priority="1",
                caller_id=2222,
                variables={"text": "⚽ Notification message ⚽"},
            ),
            call().logoff(),
            call().close(),
        ]

        assert outcome is True
