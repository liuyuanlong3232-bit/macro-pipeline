"""Read full USDA export inspections report"""
import requests
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get('https://www.ams.usda.gov/mnreports/wa_gr101.txt', timeout=15, headers=UA)
print(r.text[6000:])
