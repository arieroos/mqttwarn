# -*- coding: utf-8 -*-
# (c) 2021 The mqttwarn developers
import logging
from unittest import mock
from unittest.mock import call

from mqttwarn.model import ProcessorItem as Item
from mqttwarn.util import load_module_from_file


def test_irccat_normal_success(srv, caplog):
    import socket

    item = Item(
        target="test",
        addrs=["localhost", 12345, "#testdrive"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/irccat.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(socket.AF_INET, socket.SOCK_STREAM),
            call().connect(("localhost", 12345)),
            call().send(b"\xe2\x9a\xbd Notification message \xe2\x9a\xbd\n"),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to IRCcat: ⚽ Notification message ⚽" in caplog.messages


def test_irccat_green_success(srv, caplog):
    import socket

    item = Item(
        target="test",
        addrs=["localhost", 12345, "#testdrive"],
        message="⚽ Notification message ⚽",
        data={},
        priority=1,
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/irccat.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(socket.AF_INET, socket.SOCK_STREAM),
            call().connect(("localhost", 12345)),
            call().send(b"%GREEN\xe2\x9a\xbd Notification message \xe2\x9a\xbd\n"),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to IRCcat: %GREEN⚽ Notification message ⚽" in caplog.messages


def test_irccat_red_success(srv, caplog):
    import socket

    item = Item(
        target="test",
        addrs=["localhost", 12345, "#testdrive"],
        message="⚽ Notification message ⚽",
        data={},
        priority=2,
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/irccat.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == [
            call(socket.AF_INET, socket.SOCK_STREAM),
            call().connect(("localhost", 12345)),
            call().send(b"%RED\xe2\x9a\xbd Notification message \xe2\x9a\xbd\n"),
            call().close(),
        ]

        assert outcome is True
        assert "Sending to IRCcat: %RED⚽ Notification message ⚽" in caplog.messages


def test_irccat_config_invalid(srv, caplog):

    item = Item(
        target="test",
        addrs=["localhost", 12345],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/irccat.py")

        socket_mock = mock.MagicMock()
        module.socket.socket = socket_mock

        outcome = module.plugin(srv, item)
        assert socket_mock.mock_calls == []

        assert outcome is False
        assert "Incorrect target configuration" in caplog.messages


def test_irccat_connect_fails(srv, caplog):
    import socket

    item = Item(
        target="test",
        addrs=["localhost", 12345, "#testdrive"],
        message="⚽ Notification message ⚽",
        data={},
    )

    with caplog.at_level(logging.DEBUG):

        module = load_module_from_file("mqttwarn/services/irccat.py")

        # Make the call to `connect` raise an exception.
        mock_connection = mock.MagicMock()

        def error(*args, **kwargs):
            raise Exception("something failed")

        mock_connection.connect = error

        with mock.patch(
            "socket.socket", side_effect=[mock_connection], create=True
        ) as socket_mock:

            outcome = module.plugin(srv, item)
            assert socket_mock.mock_calls == [
                call(socket.AF_INET, socket.SOCK_STREAM),
            ]

            assert outcome is False
            assert (
                "Error sending IRCcat notification to test:localhost [12345]: something failed"
                in caplog.messages
            )
