# FakeXYZ

FakeXYZ is a Python library that generates fake addresses for various countries.

## Installation

To install the library, you can use pip:

```bash
pip install .
```

Or, if you want to install it in editable mode:

```bash
pip install -e .
```

## Usage

Here's how you can use the library to generate fake addresses:

```python
from fakexyz import FakeXYZ

# Initialize the generator
xyz = FakeXYZ()

# Get a list of available countries
available_countries = xyz.get_available_countries()
print("Available Countries:")
print(available_countries)

# Get a single random address from any country
random_address = xyz.get_random_address()
print("\nRandom Address:")
print(random_address)

# Get a single random address from a specific country (e.g., 'US')
us_address = xyz.get_random_address(country='us')
print("\nRandom US Address:")
print(us_address)

# Get 3 random addresses from any country
multiple_addresses = xyz.get_random_addresses(count=3)
print("\nThree Random Addresses:")
for address in multiple_addresses:
    print(address)

# Get 2 random addresses from a specific country (e.g., 'GB')
gb_addresses = xyz.get_random_addresses(count=2, country='gb')
print("\nTwo Random GB Addresses:")
for address in gb_addresses:
    print(address)
```

## API Usage

To run the API, first install the dependencies:

```bash
pip install -r requirements.txt
```

Then, run the API:

```bash
python api.py
```

The API will be available at `http://127.0.0.1:5000`.

### Get a random address

Send a GET request to `/api/address` with the `code` parameter.

Example:

```
http://127.0.0.1:5000/api/address?code=GB
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
