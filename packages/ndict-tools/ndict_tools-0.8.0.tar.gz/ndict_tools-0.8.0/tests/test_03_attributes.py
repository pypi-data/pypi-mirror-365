"""
Test Nested Attributes
"""

import pytest

from ndict_tools import NestedDictionary
from ndict_tools.exception import StackedKeyError

d = {
    "first": "first",
    "second": {"first": "second:first", "second": "second:second"},
    "third": "third",
}
nd = NestedDictionary(d, indent=2, strict=True)


def test_indent():
    assert nd.indent == 2


def test_len():
    assert len(nd) == 3


def test_str_outpout():
    assert (
        nd.__str__()
        == "{\n  first : first,\n  second : {\n      first : second:first,\n      second : second:second,\n  },\n  third : third,\n}"
    )


def test_values():
    assert nd["first"] == "first"
    assert nd["second"]["first"] == "second:first"
    assert nd[["second", "first"]] == "second:first"
    assert nd["second"]["second"] == "second:second"
    assert nd[["second", "second"]] == "second:second"


def test_occurrences():
    assert nd.occurrences("first") == 2
    assert nd.occurrences("second") == 3
    assert nd.occurrences("third") == 1
    assert nd.occurrences("fourth") == 0


def test_is_key():
    assert nd.is_key("first") is True
    assert nd.is_key("second") is True
    assert nd.is_key("third") is True
    assert nd.is_key("fourth") is False
    assert nd.is_key("third") is True
    with pytest.raises(StackedKeyError):
        assert nd.is_key(["fourth", ["third", "fourth"]])


def test_key_list():
    assert nd.key_list("first") == [("first",), ("second", "first")]
    assert nd.key_list("third") == [("third",)]
    with pytest.raises(StackedKeyError):
        assert nd.key_list("not_in_key")


def test_unpacked_key():
    assert ("second", "first") in nd.unpacked_keys()
    assert ("second", "second") in nd.unpacked_keys()
    assert ("third",) in nd.unpacked_keys()


def test_to_dict():
    assert d == nd.to_dict()


def test_item_list():
    assert nd.items_list("first") == ["first", "second:first"]
    assert nd.items_list("second") == ["second:first", "second:second"]
    assert nd.items_list("third") == ["third"]
    with pytest.raises(StackedKeyError):
        assert nd.items_list("not_in_key")


def test_delete_simple_key():
    with pytest.raises(KeyError):
        del nd["third"]
        value = nd["third"]


def test_delete_nested_key():
    with pytest.raises(KeyError):
        del nd["second"]
        value = nd["second"]["first"]
