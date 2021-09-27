import pytest

from nexus import NexusPage, NexusBlock, NexusText, NexusStyle


@pytest.mark.skip
def test_text_html_bold():
    text = NexusText("Hello, World!", bold=True)
    assert text.html() == "<b>Hello, World!</b>"
