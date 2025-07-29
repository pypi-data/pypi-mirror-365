from .data_loader import load_data
import random

class FakeXYZ:
    def __init__(self):
        self.data, _, self.country_name_map = load_data() # Unpack data, warnings, and country_name_map
        self.countries = list(self.data.keys())

    def _resolve_country_code(self, country_input):
        """
        Resolves a country input (code or name) to its official country code.
        Performs case-insensitive matching and suggests alternatives if not found.
        """
        if not country_input:
            return random.choice(self.countries)

        country_input_lower = country_input.lower()

        # 1. Try direct country code match
        if country_input_lower in self.countries:
            return country_input_lower
        
        # 2. Try full country name match
        if country_input_lower in self.country_name_map:
            return self.country_name_map[country_input_lower]

        # 3. Fuzzy matching for suggestions
        suggestion = None
        for code in self.countries:
            full_name = self.data[code]['meta']['country'].lower()
            if country_input_lower in full_name or full_name.startswith(country_input_lower):
                suggestion = f"{self.data[code]['meta']['country']} (Code: {code.upper()})"
                break
        
        error_message = f"Country '{country_input}' not found."
        if suggestion:
            error_message += f" Did you mean {suggestion}?"
        raise ValueError(error_message)

    def get_random_address(self, country=None):
        country_code = self._resolve_country_code(country)
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
        # Resolve country code once for multiple addresses if specified
        resolved_country_code = self._resolve_country_code(country) if country else None
        for _ in range(count):
            # Pass the resolved code or None if it was originally None
            addresses.append(self.get_random_address(resolved_country_code))
        return addresses

    def get_available_countries(self):
        return [self.data[code]['meta']['country'] for code in self.countries]
