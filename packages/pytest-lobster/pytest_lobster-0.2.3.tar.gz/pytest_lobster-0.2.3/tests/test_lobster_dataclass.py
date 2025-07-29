import pytest

from pytest_lobster.lobster import Lobster, LobsterActivity, LobsterFileReference


def test_lobster_should_not_have_item_before_added():
    lobster = Lobster()
    assert not lobster.have_item("test")


def test_lobster_should_have_item_after_added():
    lobster = Lobster()
    lobster.data.append(
        LobsterActivity(
            "pytest test",
            LobsterFileReference("test.py", None, None),
            "test::test",
            [],
            [],
            [],
            [],
            "test",
            "Test",
            None,
        )
    )
    assert lobster.have_item("test")
