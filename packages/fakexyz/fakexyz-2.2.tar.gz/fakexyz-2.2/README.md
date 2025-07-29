# FakeXYZ

FakeXYZ is a Python library designed to generate fake user and address information for various countries. It's useful for testing, data anonymization, and populating databases with realistic-looking data.

## Features

- **Multi-country Support**: Generate data for a wide range of countries.
- **Random Address Generation**: Get complete address details including street, city, state, postal code, and more.
- **User Information**: Generate names, genders, phone numbers, and avatars.
- **Fuzzy Matching for Countries**: Provides intelligent suggestions for country names and codes if the input is incorrect.

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

If you provide an incorrect country name or code, FakeXYZ will now provide suggestions:

```python
from fakexyz import FakeXYZ

xyz = FakeXYZ()

try:
    address = xyz.get_random_address(country="bangldesh") # Typo
except ValueError as e:
    print(e)
# Expected output: Country 'bangldesh' not found. Did you mean Bangladesh (Code: BD)?

try:
    address = xyz.get_random_address(country="gv") # Typo
except ValueError as e:
    print(e)
# Expected output: Country 'gv' not found. Did you mean Georgia (Code: GE)?
```

### Listing Supported Countries

```python
from fakexyz import FakeXYZ

xyz = FakeXYZ()
countries = xyz.get_available_countries()
print("Supported Countries:", countries)
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License. See the `LICENSE.txt` file for details.
