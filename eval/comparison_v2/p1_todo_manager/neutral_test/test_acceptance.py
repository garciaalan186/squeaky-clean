"""Neutral acceptance tests for P1 Todo Manager.

The `todos` fixture provides a uniform interface that adapts to whatever
entry-point shape the generated project chose (use cases, manager class,
free functions, etc.).
"""
from __future__ import annotations

import pytest


def test_create_returns_title(todos) -> None:
    todo = todos.create("Buy milk")
    assert todos.title(todo) == "Buy milk"


def test_create_starts_pending(todos) -> None:
    todo = todos.create("Task")
    assert todos.is_pending(todo) is True


def test_mark_complete_clears_pending(todos) -> None:
    todo = todos.create("Task")
    todo = todos.mark_complete(todo)
    assert todos.is_pending(todo) is False


def test_empty_title_raises(todos) -> None:
    with pytest.raises((ValueError, Exception)) as exc:
        todos.create("")
    # Reject silent acceptance — must raise some error
    assert exc.value is not None


def test_list_pending_filters_completed(todos) -> None:
    a = todos.create("a")
    b = todos.create("b")
    todos.mark_complete(b)
    pending = todos.list_pending()
    assert len(pending) == 1
