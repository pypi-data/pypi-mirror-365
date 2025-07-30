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