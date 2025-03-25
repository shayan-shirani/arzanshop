import re
import uuid

def validate_username(username):
    regex_email = r'^[a-zA-Z]+([._][a-zA-Z0-9]+)*@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
    regex_phone = r'^(\+98|98|0)9\d{9}$'
    username_type = None

    if re.match(regex_email, username):
        username_type = 'email'

    elif re.match(regex_phone, username):
        username_type = 'phone'

    return username_type

def generate_request_id():
    return uuid.uuid4()