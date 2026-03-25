import pytest
import datetime
from sitekit import rssreader
from sitekit.settings import settings


@pytest.fixture(autouse=True, scope="module")
def prova():
    return None

def test_caricamento_file(prova):
    assert prova is None