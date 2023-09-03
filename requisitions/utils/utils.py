import random
from django.utils.text import slugify


def generate_slug(text: str, slug_max_length:int):
    return slugify(text)[:slug_max_length]


def generate_unique_slug(text: str, random_suffix_length: int = 6, slug_max_length: int = 50) -> str:
    random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(random_suffix_length)])
    slug = generate_slug(text, slug_max_length)[:slug_max_length-random_suffix_length+1]

    return f'{slug}-{random_suffix}'
                        