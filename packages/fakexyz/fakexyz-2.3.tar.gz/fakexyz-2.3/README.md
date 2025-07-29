# FakeXYZ

FakeXYZ is a Python library designed to generate fake user and address information for various countries. It's useful for testing, data anonymization, and populating databases with realistic-looking data.

## Features

-   **Multi-country Support**: Generate data for a wide range of countries.
-   **Random Address Generation**: Get complete address details including street, city, state, postal code, and more.
-   **User Information**: Generate names, genders, phone numbers, and avatars.
-   **Intelligent Country Suggestions**: Provides highly relevant suggestions for country names and codes if the input is incorrect, prioritizing exact matches, best name matches, and prefix-based code matches.

## Installation

You can install FakeXYZ using pip:

```bash
pip install fakexyz
```

## Usage

### Generating a Random Address

```python
from fakexyz import FakeXYZ

xyz = FakeXYZ()

# Get a random address for a specific country (e.g., United States)
address = xyz.get_random_address(country="US")
print(address)

# Get a random address for a specific country by full name (e.g., Bangladesh)
address = xyz.get_random_address(country="Bangladesh")
print(address)

# Get multiple random addresses
addresses = xyz.get_random_addresses(count=3, country="CA")
for addr in addresses:
    print(addr)
```

### Handling Incorrect Country Input

If you provide an incorrect country name or code, FakeXYZ will now provide intelligent suggestions:

```python
from fakexyz import FakeXYZ

xyz = FakeXYZ()

try:
    address = xyz.get_random_address(country="bangldesh") # Typo
except ValueError as e:
    print(e)
# Expected output: Country 'bangldesh' not found. Did you mean?
# 🇧🇩 Bangladesh (<code>BD</code>)

try:
    address = xyz.get_random_address(country="gv") # Typo
except ValueError as e:
    print(e)
# Expected output: Country 'gv' not found. Did you mean?
# 🇬🇪 Georgia (<code>GE</code>)
# 🇬🇭 Ghana (<code>GH</code>)
# 🇬🇧 United Kingdom (<code>GB</code>)

try:
    address = xyz.get_random_address(country="zz") # No close match
except ValueError as e:
    print(e)
# Expected output: Country 'zz' not found.
# Did you mean?
# Please check the supported countries list using the `!country` command.
```

### Listing Supported Countries

```python
from fakexyz import FakeXYZ

xyz = FakeXYZ()
countries = xyz.get_available_countries()
print("Supported Countries:", countries)
```

## Supported Countries

Here is a list of countries currently supported by FakeXYZ:

*   🇦🇫 Afghanistan (AF)
*   🇦🇱 Albania (AL)
*   🇩🇿 Algeria (DZ)
*   🇦🇮 Anguilla (AI)
*   🇦🇶 Antarctica (AQ)
*   🇦🇷 Argentina (AR)
*   🇦🇲 Armenia (AM)
*   🇦🇺 Australia (AU)
*   🇦🇹 Austria (AT)
*   🇦🇿 Azerbaijan (AZ)
*   🇧🇩 Bangladesh (BD)
*   🇧🇲 Bermuda (BM)
*   🇧🇴 Bolivia (BO)
*   🇧🇹 Bhutan (BT)
*   🇧🇷 Brazil (BR)
*   🇧🇬 Bulgaria (BG)
*   🇰🇭 Cambodia (KH)
*   🇨🇲 Cameroon (CM)
*   🇨🇦 Canada (CA)
*   🇨🇱 Chile (CL)
*   🇨🇳 China (CN)
*   🇨🇴 Colombia (CO)
*   🇨🇿 Czechia (CZ)
*   🇩🇰 Denmark (DK)
*   🇪🇬 Egypt (EG)
*   🇫🇮 Finland (FI)
*   🇫🇷 France (FR)
*   🇬🇪 Georgia (GE)
*   🇩🇪 Germany (DE)
*   🇬🇭 Ghana (GH)
*   🇬🇷 Greece (GR)
*   🇬🇱 Greenland (GL)
*   🇬🇹 Guatemala (GT)
*   🇭🇰 Hong Kong (HK)
*   🇮🇸 Iceland (IS)
*   🇮🇳 India (IN)
*   🇮🇩 Indonesia (ID)
*   🇮🇶 Iraq (IQ)
*   🇮🇪 Ireland (IE)
*   🇮🇱 Israel (IL)
*   🇮🇹 Italy (IT)
*   🇯🇵 Japan (JP)
*   🇯🇴 Jordan (JO)
*   🇰🇿 Kazakhstan (KZ)
*   🇰🇪 Kenya (KE)
*   🇧🇭 Kingdom of Bahrain (BH)
*   🇧🇪 Kingdom of Belgium (BE)
*   🇱🇧 Lebanon (LB)
*   🇲🇾 Malaysia (MY)
*   🇲🇻 Maldives (MV)
*   🇲🇷 Mauritania (MR)
*   🇲🇽 Mexico (MX)
*   🇲🇦 Morocco (MA)
*   🇲🇲 Myanmar (MM)
*   🇳🇵 Nepal (NP)
*   🇳🇱 Netherlands (NL)
*   🇳🇿 New Zealand (NZ)
*   🇳🇪 Niger (NE)
*   🇳🇬 Nigeria (NG)
*   🇳🇴 Norway (NO)
*   🇴🇲 Oman (OM)
*   🇵🇰 Pakistan (PK)
*   🇵🇸 Palestine (PS)
*   🇵🇦 Panama (PA)
*   🇵🇪 Peru (PE)
*   🇵🇭 Philippines (PH)
*   🇵🇱 Poland (PL)
*   🇵🇹 Portugal (PT)
*   🇶🇦 Qatar (QA)
*   🇷🇴 Romania (RO)
*   🇷🇺 Russia (RU)
*   🇸🇲 San Marino (SM)
*   🇸🇦 Saudi Arabia (SA)
*   🇸🇬 Singapore (SG)
*   🇿🇦 South Africa (ZA)
*   🇰🇷 South Korea (KR)
*   🇪🇸 Spain (ES)
*   🇱🇰 Sri Lanka (LK)
*   🇸🇩 Sudan (SD)
*   🇸🇪 Sweden (SE)
*   🇨🇭 Switzerland (CH)
*   🇹🇼 Taiwan (TW)
*   🇹🇿 Tanzania (TZ)
*   🇹🇭 Thailand (TH)
*   🇹🇷 Turkiye (TR)
*   🇺🇬 Uganda (UG)
*   🇺🇦 Ukraine (UA)
*   🇦🇪 United Arab Emirates (AE)
*   🇬🇧 United Kingdom (GB)
*   🇺🇸 United States (US)
*   🇻🇪 Venezuela (VE)
*   🇻🇳 Vietnam (VN)
*   🇾🇪 Yemen (YE)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE.txt` file for details.
