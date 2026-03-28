from urllib.parse import urlparse

def valid_length(value, min_len, max_len, field_name):
    if not (min_len <= len(value) <= max_len):
        return False, f"{field_name} must be between {min_len} and {max_len} characters."

    return True, None

def is_safe_url(target):
    return urlparse(target).netloc == ''