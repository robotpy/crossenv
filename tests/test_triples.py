#################################################
# Compiler triple parsing (no crossenv required)
#################################################

from crossenv import CrossEnvBuilder


def test_split_apple_os_version():
    expected = {
        "ios13.0": ("ios", "13.0"),
        "ios": ("ios", ""),
        "tvos17.0": ("tvos", "17.0"),
        "tvos": ("tvos", ""),
        "watchos10.0": ("watchos", "10.0"),
        "watchos": ("watchos", ""),
        "darwin23.4.0": ("darwin", "23.4.0"),
        "darwin": ("darwin", ""),
        # Previously rejected as unknown
        "macos14.0": ("macos", "14.0"),
        "macosx14.0": ("macosx", "14.0"),
        "xros1.0": ("xros", "1.0"),
    }
    actual = {
        value: CrossEnvBuilder._split_apple_os_version(value) for value in expected
    }
    assert actual == expected


def test_clean_triple():
    expected = {
        # Apple: arm64 -> aarch64, OS version removed. The clang -dumpmachine
        # and HOST_GNU_TYPE forms must clean to the same value.
        "arm64-apple-ios13.0": ["aarch64", "apple", "ios"],
        "aarch64-apple-ios": ["aarch64", "apple", "ios"],
        "arm64-apple-tvos17.0": ["aarch64", "apple", "tvos"],
        "arm64-apple-watchos10.0": ["aarch64", "apple", "watchos"],
        "arm64-apple-darwin23.4.0": ["aarch64", "apple", "darwin"],
        "aarch64-apple-darwin": ["aarch64", "apple", "darwin"],
        "x86_64-apple-darwin23.4.0": ["x86_64", "apple", "darwin"],
        # Apple simulator: 4 parts, not compared
        "arm64-apple-ios13.0-simulator": None,
        # Non-Apple: vendor dropped from 4-part triples
        "x86_64-linux-gnu": ["x86_64", "linux", "gnu"],
        "x86_64-pc-linux-gnu": ["x86_64", "linux", "gnu"],
        "aarch64-unknown-linux-gnu": ["aarch64", "linux", "gnu"],
        # Other forms
        "x86_64": None,
        "aarch64-linux": None,
        "a-b-c-d-e": None,
    }
    actual = {triple: CrossEnvBuilder._clean_triple(triple) for triple in expected}
    assert actual == expected
