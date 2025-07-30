import random
import string
import secrets


def generate_id(length:int = 8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))