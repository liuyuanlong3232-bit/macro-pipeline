"""Test the new export inspections scraper"""
import sys; sys.path.insert(0, '.')
from data_scrapers import fetch_usda_export_inspections
result = fetch_usda_export_inspections()
print(result)
