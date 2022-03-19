"""To check for completion, google slides will be output as html files and
checksummed. This test takes an example case, whose files are included in ./fixtures,
and provides a proof of concept for this method."""

from hashlib import md5
from pathlib import Path

import pytest

FIXTURES = Path(Path(__file__).parent, "fixtures")

TEMPLATE = FIXTURES / "slide_template.html"
COMPLETE = FIXTURES / "slide_completed.html"
INCOMPLETE = FIXTURES / "slide_incomplete.html"


@pytest.fixture
def template_content() -> str:
    with open(TEMPLATE, "r") as fp:
        return fp.read()


@pytest.fixture
def complete_content() -> str:
    with open(COMPLETE, "r") as fp:
        return fp.read()


@pytest.fixture
def incomplete_content() -> str:
    with open(INCOMPLETE, "r") as fp:
        return fp.read()


def test_incomplete_matches_template(template_content, incomplete_content):
    md5(bytes(template_content, "utf8")) == md5(bytes(incomplete_content, "utf8"))


def test_complete_does_not_match_template(template_content, complete_content):
    md5(bytes(template_content, "utf8")) == md5(bytes(complete_content, "utf8"))
