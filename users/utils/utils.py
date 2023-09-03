import random, string


def generate_random_username(random_suffix_length: int) -> str:
    chars = string.ascii_letters + string.digits
    user = "usuario_"
    suffix = "".join([random.choice(chars) for _ in range(random_suffix_length)])
    return f"{user}{suffix}"


def generate_random_password(random_password_length: int) -> str:
    chars = string.ascii_letters + string.digits
    random_password = "".join(
        [random.choice(chars) for _ in range(random_password_length)]
    )
    return random_password
