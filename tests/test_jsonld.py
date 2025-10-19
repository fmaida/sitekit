import pytest
from sitekit import jsonld, configurazioni


@pytest.fixture(autouse=True, scope="module")
def vuoto_output():
    jsonld.clear()
    return jsonld.debug()

@pytest.fixture(autouse=True, scope="module")
def pieno_output():
    jsonld.clear()
    data = configurazioni.carica("demo", "it")
    jsonld.import_(data)
    return jsonld.debug()

def test_oggetti_creati(vuoto_output):
    assert vuoto_output != {}

def test_ristorante_come_default(vuoto_output):
    assert vuoto_output["@type"] == "Restaurant"

#def test_se_vuoto_nessun_orario_di_apertura(vuoto_output):
#    assert vuoto_output["openingHours"] == []

def test_se_pieno_presente_indirizzo(pieno_output):
    assert pieno_output["name"] != ""
    assert pieno_output["address"]["streetAddress"] != ""
    assert pieno_output["address"]["addressLocality"] != ""

#def test_se_pieno_orario_di_apertura(pieno_output):
#    assert pieno_output["openingHoursSpecification"] != []