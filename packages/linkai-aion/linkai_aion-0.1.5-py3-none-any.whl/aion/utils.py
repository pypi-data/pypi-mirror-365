### aion/utils.py
import re
import uuid
import hashlib

from IPython.utils.PyColorize import pride_theme


def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes} min {seconds} sec"

def random_string(length=8):
    import random, string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def slugify(text):
    return text.strip().lower().replace(" ", "-")




def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+",email) is not None


def generate_uuid():
    return str(uuid.uuid4())


def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()




def get_even_numbers(numbers):
    return [n for n in numbers if n % 2 == 0]

def get_odd_numbers(numbers):
    return [n for n in numbers if n % 2 != 0]