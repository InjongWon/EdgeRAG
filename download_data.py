#!/usr/bin/env python3
"""
download_data.py - Create sample financial document for testing
"""

from pathlib import Path

# Create data directory
Path("data").mkdir(exist_ok=True)

# Create a sample test document
sample_doc = """
TESLA, INC.
FORM 10-K
ANNUAL REPORT
For the fiscal year ended December 31, 2023

RISK FACTORS

Our business is subject to numerous risks. Key risks include:

1. Supply Chain Risks: We depend on a limited number of suppliers for critical components. 
   Any disruption could significantly impact our production capabilities.

2. Regulatory Risks: Changes in automotive safety regulations, emissions standards, 
   and autonomous driving regulations could increase our costs or limit our operations.

3. Competition: The automotive industry is highly competitive. Traditional automakers 
   and new entrants are investing heavily in electric vehicles.

4. Technology Risks: Our Full Self-Driving technology is still under development. 
   Delays or technical challenges could impact customer adoption.

FINANCIAL PERFORMANCE

Revenue: Total revenues increased to $96.7 billion in 2023, up from $81.5 billion in 2022.

Operating Income: Operating income was $8.9 billion, representing a 9.2% operating margin.

Cash Position: We ended 2023 with $29.1 billion in cash and cash equivalents.

BUSINESS STRATEGY

Our strategy focuses on:
- Scaling production to meet growing demand
- Reducing production costs through manufacturing innovation
- Expanding our Supercharger network globally
- Advancing autonomous driving capabilities
- Growing our energy storage business
"""

with open("data/SAMPLE_TSLA_10K.txt", "w") as f:
    f.write(sample_doc)

print("Created sample document: data/SAMPLE_TSLA_10K.txt")
print("Use this to test your pipeline")
print()
print("To download real 10K PDFs:")
print("1. Visit: https://www.sec.gov/edgar/searchedgar/companysearch")
print("2. Search for: TSLA, AAPL, MSFT")
print("3. Download their latest 10K filings to data/ folder")
