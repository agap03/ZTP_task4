import pytest
from src.literature.pubmed_fetch import normalize_pubmed_record

# Testy dla funkcji normalize_pubmed_record w pubmed_fetch.py
def test_normalize_pubmed_record_basic():
    record = {
        "Id": "12345",
        "Title": "Test Paper",
        "PubDate": "2024 Jan 15",
        "FullJournalName": "Journal of Testing",
        "Authors": [{"Name": "Smith J"}, {"Name": "Doe A"}]
    }

    normalized = normalize_pubmed_record(record)

    assert normalized["PMID"] == "12345"
    assert normalized["title"] == "Test Paper"
    assert normalized["year"] == "2024"  # sprawdzamy parsowanie roku
    assert normalized["journal"] == "Journal of Testing"
    assert normalized["authors"] == "Smith J; Doe A"

# Testy dla przypadków z brakującymi polami
def test_normalize_pubmed_record_missing_fields():
    record = {
        "Id": "67890",
        # brak Title
        "PubDate": "2023",
        # brak FullJournalName
        "Authors": []
    }

    normalized = normalize_pubmed_record(record)

    assert normalized["PMID"] == "67890"
    assert normalized["title"] is None
    assert normalized["year"] == "2023"
    assert normalized["journal"] is None
    assert normalized["authors"] == ""

# Test bez daty publikacji
def test_normalize_pubmed_record_empty_pubdate():
    record = {
        "Id": "11111",
        "Title": "No Date Paper",
        "PubDate": "",
        "FullJournalName": "Journal of Missing Dates",
        "Authors": [{"Name": "Alice"}]
    }

    normalized = normalize_pubmed_record(record)

    assert normalized["year"] == ""  # jeśli brak daty, rok też pusty
