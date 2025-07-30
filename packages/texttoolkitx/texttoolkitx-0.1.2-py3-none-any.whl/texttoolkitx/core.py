import re
import random
import string

def slugify(text: str) -> str:
    # Convert to lowercase, remove non-alphanumeric, replace spaces with hyphens
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s]+', '-', text).strip('-')

def truncate(text: str, length: int = 100) -> str:
    return text if len(text) <= length else text[:length].rstrip() + '...'

def is_palindrome(text: str) -> bool:
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    return cleaned == cleaned[::-1]

def random_string(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
