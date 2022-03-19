import pytest

from ..doc_writer import DocWriter, Page


@pytest.fixture
def writer():
    return DocWriter()


def test_add_page(writer):
    writer.add_page(Page(student="joey", wk_19_grade=10, wk_20_grade=15, wk_21_grade=0))

    # a table was added
    assert len(writer.doc.tables) == 2
    assert writer.doc.paragraphs[7].text == "Name: joey"
    assert writer.doc.tables[1].rows[1].cells[-1].paragraphs[0].text == "10"
    assert writer.doc.tables[1].rows[2].cells[-1].paragraphs[0].text == "15"
    assert writer.doc.tables[1].rows[3].cells[-1].paragraphs[0].text == "0"


def test_page_with_notes(writer):
    writer.add_page(
        Page(
            student="tim",
            wk_19_grade=10,
            wk_20_grade=15,
            wk_21_grade=15,
            notes="You can do better than that, tim",
        )
    )
    assert (
        writer.doc.paragraphs[-1].text
        == "Notes: You can do better than that, tim"
        in [p.text for p in writer.doc.paragraphs]
    )


def test_add_pages(writer):
    writer.add_pages(
        [
            Page(student="joey", wk_19_grade=10, wk_20_grade=15, wk_21_grade=0),
            Page(student="timmy", wk_19_grade=10, wk_20_grade=20, wk_21_grade=0),
            Page(student="tammy", wk_19_grade=15, wk_20_grade=20, wk_21_grade=15),
            Page(
                student="tummy",
                wk_19_grade=20,
                wk_20_grade=20,
                wk_21_grade=20,
                notes="Awesome work!",
            ),
        ]
    )

    assert len(writer.doc.tables) == 5
    # spot check data
    assert writer.doc.tables[1].rows[1].cells[-1].text == "10"
