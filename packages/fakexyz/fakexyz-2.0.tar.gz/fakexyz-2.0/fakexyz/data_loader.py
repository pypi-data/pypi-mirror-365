import os
import json

def _validate_data_structure(data, filename, warnings_list):
    """
    Validates the structure of the loaded JSON data for a given country.
    Checks for the presence of expected keys in 'meta' and 'addresses' sections.
    Appends warnings to the provided warnings_list.
    """
    country_code = filename.split(".")[0]
    
    # Validate 'meta' section
    expected_meta_keys = ["country", "country_code", "country_flag", "currency"]
    if "meta" not in data:
        warnings_list.append(f"Warning: '{filename}' is missing 'meta' section.")
        return
    for key in expected_meta_keys:
        if key not in data["meta"]:
            warnings_list.append(f"Warning: '{filename}' meta section is missing key: '{key}'")

    # Validate 'addresses' section
    expected_address_keys = [
        "name", "gender", "phone_number", "street_address", "street_name",
        "building_number", "city", "state", "postal_code", "timezone", "avatar_url"
    ]
    if "addresses" not in data:
        warnings_list.append(f"Warning: '{filename}' is missing 'addresses' section.")
        return
    
    for i, address in enumerate(data["addresses"]):
        for key in expected_address_keys:
            if key not in address:
                warnings_list.append(f"Warning: '{filename}' address entry {i} is missing key: '{key}'")
        
        # Validate 'timezone' sub-keys if 'timezone' exists
        if "timezone" in address:
            if "offset" not in address["timezone"]:
                warnings_list.append(f"Warning: '{filename}' address entry {i} timezone is missing key: 'offset'")
            if "description" not in address["timezone"]:
                warnings_list.append(f"Warning: '{filename}' address entry {i} timezone is missing key: 'description'")


def load_data():
    data = {}
    warnings_list = []
    country_name_map = {}
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "data")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            country_code = filename.split(".")[0]
            file_path = os.path.join(data_dir, filename)
            with open(file_path, encoding="utf-8") as f:
                country_data = json.load(f)
                data[country_code] = country_data
                _validate_data_structure(country_data, filename, warnings_list) # Validate after loading
                
                # Add full country name to map
                if "meta" in country_data and "country" in country_data["meta"]:
                    full_country_name = country_data["meta"]["country"].lower()
                    country_name_map[full_country_name] = country_code
    return data, warnings_list, country_name_map
