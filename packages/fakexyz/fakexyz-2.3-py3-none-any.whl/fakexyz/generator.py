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

        # 1. Prioritize exact matches (case-insensitive)
        for country_data in self.supported_countries_list:
            if country_data["country"].lower() == user_input_lower or \
               country_data["country_code"].lower() == user_input_lower:
                return [f"{country_data['country_flag']} {country_data['country']} (<code>{country_data['country_code']}</code>)"]

        # 2. Fuzzy matching for country names (single best match if very high score)
        country_names = {c["country"]: c for c in self.supported_countries_list}
        name_matches = process.extract(user_input, country_names.keys(), limit=1)
        if name_matches and name_matches[0][1] >= 85: # High confidence match
            country_data = country_names[name_matches[0][0]]
            return [f"{country_data['country_flag']} {country_data['country']} (<code>{country_data['country_code']}</code>)"]

        # 3. Broad Prefix Matching (Country Code and Name)
        prefix_matches = []
        # First, try to match the full user input as a prefix
        for country_data in self.supported_countries_list:
            if country_data["country_code"].lower().startswith(user_input_lower) or \
               country_data["country"].lower().startswith(user_input_lower):
                prefix_matches.append(f"{country_data['country_flag']} {country_data['country']} (<code>{country_data['country_code']}</code>)")
        
        # If no direct prefix matches, and input is not empty, try matching by the first character
        if not prefix_matches and user_input_lower:
            first_char_lower = user_input_lower[0]
            for country_data in self.supported_countries_list:
                if country_data["country_code"].lower().startswith(first_char_lower) or \
                   country_data["country"].lower().startswith(first_char_lower):
                    prefix_matches.append(f"{country_data['country_flag']} {country_data['country']} (<code>{country_data['country_code']}</code>)")

        if prefix_matches:
            # If any prefix matches are found (either full input or first char), return all unique ones, sorted.
            return sorted(list(dict.fromkeys(prefix_matches)))

        # 4. Fallback to general fuzzy matching for codes and names
        all_searchable_terms = [c["country"] for c in self.supported_countries_list] + \
                               [c["country_code"] for c in self.supported_countries_list]
        
        fuzzy_matches = process.extract(user_input, all_searchable_terms, limit=limit)
        
        for match, score in fuzzy_matches:
            if score >= 60: # Only consider matches with a reasonable score
                found_country_data = None
                for country_data in self.supported_countries_list:
                    if country_data["country"] == match or country_data["country_code"] == match:
                        found_country_data = country_data
                        break
                
                if found_country_data and f"{found_country_data['country_flag']} {found_country_data['country']} (<code>{found_country_data['country_code']}</code>)" not in suggestions:
                    suggestions.append(f"{found_country_data['country_flag']} {found_country_data['country']} (<code>{found_country_data['country_code']}</code>)")
        
        if suggestions:
            return sorted(list(dict.fromkeys(suggestions)))[:limit]

        # 5. If no suggestions at all, suggest seeing all countries
        return ["Please check the supported countries list using the `!country` command."]

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
