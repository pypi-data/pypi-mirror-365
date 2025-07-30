import time
import requests

def convert_blob_to_raw_github_url(blob_url: str) -> str:
    """
    Converts a GitHub "blob" URL to a "raw" content URL.

    GitHub blob URL:
        https://github.com/{user}/{repo}/blob/{branch}/{path}
    Converted raw URL:
        https://github.com/{user}/{repo}/raw/{branch}/{path}

    Args:
        blob_url (str): The GitHub blob URL to convert.

    Returns:
        str: The converted raw GitHub URL.

    Raises:
        ValueError: If the input URL does not contain "/blob/".
    """
    blob_segment = "/blob/"
    raw_segment = "/raw/"

    if blob_segment not in blob_url:
        raise ValueError(f"❌ input does not contain {blob_segment}: {blob_url}")

    return blob_url.replace(blob_segment, raw_segment, 1)

def validate_Windows_filename_with_reasons(name: str) -> dict:
    """
    Validates a Windows filename against Microsoft's file naming restrictions.

    The validation uses a JSON ruleset hosted on GitHub, which defines:
    - Disallowed characters and their classification into character groups
    - Reserved device names (e.g., CON, NUL, COM1)
    - Forbidden trailing characters (space and period)

    The JSON is retrieved via HTTP with up to 100 retries using the `requests` library.

    Args:
        name (str): The filename to validate (can include extension, e.g., "nul.txt").

    Returns:
        dict: A dictionary describing the validation result:
            If the filename is valid:
                {
                    "valid": True
                }
            If the filename is invalid:
                {
                    "valid": False,
                    "problems": [
                        {
                            "character": "<offending character or name>",
                            "reason": "<explanation of the problem>"
                        },
                        ...
                    ]
                }

    Raises:
        RuntimeError: If the GitHub-hosted rules file cannot be retrieved after 100 attempts.
        ValueError: If the GitHub blob URL is malformed.
    """
    # GitHub blob URL containing the JSON rules
    blob_url = (
        "https://github.com/PeterCullenBurbery/windows-file-name-rules/blob/main/"
        "file_names/file-names-002/windows_filename_rules.json"
    )

    # Convert to raw content URL
    raw_url = convert_blob_to_raw_github_url(blob_url)

    # Attempt to download the JSON with retry logic
    for attempt in range(1, 101):
        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                break
            else:
                raise requests.HTTPError(f"Status code {response.status_code}")
        except Exception as e:
            if attempt == 100:
                raise RuntimeError(f"❌ Failed to load JSON after 100 attempts: {e}")
            time.sleep(0.5)

    # Build lookup tables
    char_id_to_char = {entry["id"]: entry["char"] for entry in data["table_of_characters"]}
    char_to_id = {
        entry["char"]: entry["id"]
        for entry in data["table_of_characters"]
        if not entry["file"]
    }
    group_id_to_description = {
        entry["id"]: entry["description"] for entry in data["table_of_groups_of_characters"]
    }
    char_id_to_group_id = {
        entry["character_id"]: entry["group_id"]
        for entry in data["table_of_characters_in_groups"]
    }
    reserved_names_dict = {
        entry["name"]: entry["reason"] for entry in data["reserved_names"]
    }

    # Track invalid characters and reasons
    invalids = []

    # Reason 1: Disallowed characters
    for char in name:
        if char in char_to_id:
            char_id = char_to_id[char]
            group_id = char_id_to_group_id.get(char_id)
            reason = group_id_to_description.get(group_id, "Disallowed character")
            invalids.append((char, reason))

    # Reason 2: Ends with space or period
    if name.endswith(" ") or name.endswith("."):
        invalids.append((
            name[-1],
            "File or folder names cannot end with a space or period (.)"
        ))

    # Reason 3: Reserved device names
    base_name = name.split('.')[0].upper()
    if base_name in reserved_names_dict:
        invalids.append((
            base_name,
            reserved_names_dict[base_name]
        ))

    # Return result
    if not invalids:
        return {"valid": True}
    else:
        return {
            "valid": False,
            "problems": [
                {"character": c, "reason": r} for c, r in invalids
            ]
        }
    
def valid_Windows_filename(name: str) -> bool:
    """
    Checks whether a given filename is valid according to Windows naming rules.

    This function is a simplified wrapper around `validate_Windows_filename_with_reasons`
    that returns only a boolean indicating validity.

    Args:
        name (str): The filename to check.

    Returns:
        bool: True if the filename is valid, False otherwise.
    """
    result = validate_Windows_filename_with_reasons(name)
    return result["valid"]