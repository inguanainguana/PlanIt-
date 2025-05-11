import uuid


def generate_confirmation_link():
    return str(uuid.uuid4())
