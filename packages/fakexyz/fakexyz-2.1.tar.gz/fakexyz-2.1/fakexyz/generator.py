from .data_loader import load_data
import random
from fuzzywuzzy import process # Import fuzzywuzzy

class FakeXYZ:
    def __init__(self):
        self.data, _, self.country_name_map = load_data() # Unpack data, warnings, and country_name_map
        self.countries = list(self.data.keys())
        
        # Pre-load supported countries for suggestions
        self.supported_countries_list = []
        for code in self.countries:
            meta = self.data[code]['meta']
            self.supported_countries_list.append({
                "country": meta["country"],
                "country_code": meta["country_code"].upper(),
                "country_flag": meta.get("country_flag", "")
            })

    def _get_suggestions(self, user_input, limit=3):
        suggestions = []
        user_input_lower = user_input.lower()

        # Fuzzy matching for country names
        country_names = {c["country"]: c for c in self.supported_countries_list}
        name_matches = process.extract(user_input, country_names.keys(), limit=limit)
        for match, score in name_matches:
            if score >= 70: # Threshold for good match
                country_data = country_names[match]
                suggestions.append(f"{country_data['country_flag']} {country_data['country']} (<code>{country_data['country_code']}</code>)")

        # Fuzzy matching for country codes
        country_codes = {c["country_code"]: c for c in self.supported_countries_list}
        code_matches = process.extract(user_input, country_codes.keys(), limit=limit)
        for match, score in code_matches:
            if score >= 70 and f"{country_codes[match]['country_flag']} {country_codes[match]['country']} (<code>{country_codes[match]['country_code']}</code>)" not in suggestions: # Avoid duplicates
                country_data = country_codes[match]
                suggestions.append(f"{country_data['country_flag']} {country_data['country']} (<code>{country_data['country_code']}</code>)")
        
        return suggestions

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

        # If not found, provide suggestions
        suggestions = self._get_suggestions(country_input)
        
        error_message = f"Country '{country_input}' not found."
        if suggestions:
            suggestion_text = "\n".join(suggestions)
            error_message += f"\n\nDid you mean?\n{suggestion_text}"
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
