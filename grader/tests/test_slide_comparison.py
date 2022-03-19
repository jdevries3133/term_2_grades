"""To check for completion, google slides will be output as html files and
checksummed. This test takes an example case, whose files are included in ./fixtures,
and provides a proof of concept for this method."""

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
    assert template_content == incomplete_content


def test_complete_does_not_match_template(template_content, complete_content):
    assert template_content != complete_content
