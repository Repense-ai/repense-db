import hashlib
import re


def generate_hash(password: str) -> hash:
    encode = password.encode()
    password_hash = hashlib.sha256(encode).hexdigest()

    return password_hash


def check_valid_password(password: str) -> bool:

    error_dict = {
        "length": False,
        "uppercase": False,
        "lowercase": False,
        "number": False,
        "special": False,
    }

    if len(password) < 6 or len(password) > 20:
        error_dict["length"] = True
    if not re.search(r"[A-Z]", password):
        error_dict["uppercase"] = True
    if not re.search(r"[a-z]", password):
        error_dict["lowercase"] = True
    if not re.search(r"[0-9]", password):
        error_dict["number"] = True
    if not re.search(r"[\W_]", password):
        error_dict["special"] = True

    return error_dict


def format_password_error_message(error_dict: dict) -> str:
    error_message = ""

    if error_dict["length"]:
        error_message += "A senha deve ter entre 6 e 20 caracteres\n"
    if error_dict["uppercase"]:
        error_message += "A senha deve ter pelo menos uma letra maiúscula\n"
    if error_dict["lowercase"]:
        error_message += "A senha deve ter pelo menos uma letra minúscula\n"
    if error_dict["number"]:
        error_message += "A senha deve ter pelo menos um número\n"
    if error_dict["special"]:
        error_message += "A senha deve ter pelo menos um caractere especial\n"

    return error_message
