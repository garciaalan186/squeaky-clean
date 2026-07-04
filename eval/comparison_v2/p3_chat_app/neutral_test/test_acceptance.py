"""Neutral acceptance tests for P3 Chat App."""
from __future__ import annotations

import pytest


def test_create_user_returns_name(chat) -> None:
    user = chat.create_user("Alice")
    assert chat.name_of(user) == "Alice"


def test_create_room_returns_name(chat) -> None:
    room = chat.create_room("General")
    assert chat.name_of(room) == "General"


def test_join_room_increments_member_count(chat) -> None:
    alice = chat.create_user("Alice")
    room = chat.create_room("General")
    room = chat.join_room(alice, room) or room
    assert chat.member_count(room) == 1


def test_send_message_increments_message_count(chat) -> None:
    alice = chat.create_user("Alice")
    room = chat.create_room("General")
    room = chat.join_room(alice, room) or room
    chat.send_message(alice, room, "Hello")
    assert chat.message_count(room) == 1


def test_get_history_returns_one_message(chat) -> None:
    alice = chat.create_user("Alice")
    room = chat.create_room("General")
    room = chat.join_room(alice, room) or room
    chat.send_message(alice, room, "Hello")
    history = chat.get_history(room)
    assert len(history) == 1


def test_non_member_send_raises(chat) -> None:
    bob = chat.create_user("Bob")
    room = chat.create_room("General")
    # Bob is NOT joined
    with pytest.raises(ValueError):
        chat.send_message(bob, room, "Hello")


def test_empty_content_raises(chat) -> None:
    alice = chat.create_user("Alice")
    room = chat.create_room("General")
    room = chat.join_room(alice, room) or room
    with pytest.raises(ValueError):
        chat.send_message(alice, room, "")
