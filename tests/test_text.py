from vrybot.text import split_message, strip_name_prefix


def test_strip_plain_prefix():
    assert strip_name_prefix("VryBot: hello", ["VryBot"]) == "hello"


def test_strip_bold_prefix_case_insensitive():
    assert strip_name_prefix("**vrybot:** hello", ["VryBot"]) == "hello"


def test_keeps_text_without_prefix():
    assert strip_name_prefix("hello VryBot: there", ["VryBot"]) == "hello VryBot: there"


def test_short_message_is_one_chunk():
    assert split_message("hi") == ["hi"]


def test_long_message_splits_on_words_under_limit():
    text = " ".join(["word"] * 1000)
    parts = split_message(text, limit=100)
    assert all(len(p) <= 100 for p in parts)
    assert " ".join(parts) == text


def test_unbreakable_text_is_hard_cut():
    parts = split_message("x" * 250, limit=100)
    assert [len(p) for p in parts] == [100, 100, 50]
