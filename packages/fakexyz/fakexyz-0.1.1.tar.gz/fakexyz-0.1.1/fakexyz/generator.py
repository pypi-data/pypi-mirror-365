from .data_loader import load_data
import random

class FakeXYZ:
    def __init__(self):
        self.data = load_data()
        self.countries = list(self.data.keys())

    def get_random_address(self, country=None):
        if country:
            country_code = country.lower()
            if country_code not in self.countries:
                raise ValueError(f"Country code '{country}' not found.")
        else:
            country_code = random.choice(self.countries)

        country_data = self.data[country_code]
        address = random.choice(country_data['addresses'])
        
        return {
            "country": country_data['meta']['country'],
            "country_code": country_data['meta']['country_code'],
            "country_flag": country_data['meta']['country_flag'],
            "currency": country_data['meta']['currency'],
            "name": address['name'],
            "gender": address['gender'],
            "phone_number": address['phone_number'],
            "street_address": address['street_address'],
            "street_name": address['street_name'],
            "building_number": address['building_number'],
            "city": address['city'],
            "state": address['state'],
            "postal_code": address['postal_code'],
            "time_zone": address['timezone']['offset'],
            "description": address['timezone']['description'],
            "avatar_url": address['avatar_url'],
        }

    def get_random_addresses(self, count=1, country=None):
        addresses = []
        for _ in range(count):
            addresses.append(self.get_random_address(country))
        return addresses

    def get_available_countries(self):
        return self.countries
