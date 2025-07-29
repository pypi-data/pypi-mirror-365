import random
import string


def generate_token(length=32):
    """
    Generate a random token of specified length.

    :param length: Length of the token to generate
    :return: Randomly generated token as a string
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


