from src.scraper import scrape
import os

def test_generate_fake_rows():
    d = scrape.generate_fake_rows(5)
    assert "values" in d and len(d["values"]) == 5
