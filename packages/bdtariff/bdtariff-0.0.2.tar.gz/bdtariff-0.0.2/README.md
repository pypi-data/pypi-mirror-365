# BD Tariff

This project provides a Python interface to access tariff rates and calculate duties based on the Bangladesh Customs Tariff for the fiscal year 2025-2026. The tariff data is sourced from the official document: [Tariff 2025-2026 (02-06-2025).pdf](https://customs.gov.bd/files/Tariff-2025-2026(02-06-2025).pdf).

## Installation

(Add installation instructions here, e.g., `pip install bdtariff` if you plan to publish it to PyPI, or instructions for cloning the repository and setting it up locally.)

## How to Get Total Duty

To calculate the total duty for a given HSCode and assess value:

```python
from bdtariff import duty

duty()
When prompted, enter the HSCode and then the Assess Value in BDT. The function will return the total duty in BDT.

How to Know Tariff Rate
To retrieve the individual tariff rates for a specific HSCode:

Python

from bdtariff import rate

rate()
When prompted, enter the HSCode. The function will display the applicable tariff rates.

How to Get Tariff Details One by One
You can also access the individual tariff components and description for a given HSCode programmatically:

Python

from bdtariff import hscode

# Replace "HSCODE" with the actual 8-digit HSCode
result = hscode("HSCODE")

if result:
    print(result.cd)            # Get the 'cd' (Customs Duty) field
    print(result.sd)            # Get the 'sd' (Supplementary Duty) field
    print(result.rd)            # Get the 'rd' (Regulatory Duty) field
    print(result.vat)           # Get the 'vat' (Value Added Tax) field
    print(result.at)            # Get the 'at' (Advance Tax) field
    print(result.ait)           # Get the 'ait' (Advance Income Tax) field
    print(result.tti)           # Get the 'tti' (Total Taxable Imports) field - Note: This might be a calculated value, confirm its exact meaning in your context.
    print(result.tarriff_description) # Get the 'Tariff Description' field
    print(result.as_dict())     # Get all available fields as a dictionary
else:
    print("HSCode not found")
Sample Program
Here's a complete example demonstrating how to use the hscode function:

Python

from bdtariff import hscode

result = hscode("01012100") # Example HSCode for live horses, purebred breeding

if result:
    print(f"Customs Duty (CD): {result.cd}")
    print(f"Supplementary Duty (SD): {result.sd}")
    print(f"All Tariff Details: {result.as_dict()}")
else:
    print("HSCode not found")