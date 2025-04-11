import logging
import requests
import re

from repensedb.aws.secrets_manager import SecretsManager
from repensedb.utils.logs import LOGGING_CONFIG


logging.basicConfig(**LOGGING_CONFIG)


def check_valid_phone(telefone: str) -> bool:
    # Remove any non-digit characters
    phone_numbers_only = re.sub(r"\D", "", telefone)

    if len(phone_numbers_only) != 11:
        return False

    # Check if the area code is valid (11-99)
    area_code = int(phone_numbers_only[:2])
    if area_code < 11 or area_code > 99:
        return False

    # If it's a mobile number (11 digits), check if it starts with 9
    if len(phone_numbers_only) == 11 and phone_numbers_only[2] != "9":
        return False

    return True


def check_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))


def get_address_with_cep(cep: str) -> dict:

    cep = re.sub(r"[^\d]", "", cep)

    if len(cep) != 8:
        return {"error": "CEP_ERROR"}

    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")

        if response.status_code == 200 and not response.json().get("erro"):
            return response.json()
    except Exception as e:
        logging.error(f"Erro ao criar coletar endereço: {e}")
        return {"error": "ADDRESS_ERROR"}


def format_address(address: dict) -> str:

    numero = address.get("numero")
    numero_str = f"{numero} - " if numero else ""

    address_string = (
        f"{address.get('logradouro')}, "
        + numero_str
        + f"{address.get('bairro')}, "
        + f"{address.get('localidade')} - "
        + f"{address.get('uf')}, "
        + f"{address.get('cep')}"
    )

    return address_string


def get_lat_long_from_address(address: str) -> dict:
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        secrets = SecretsManager("database", "us-east-2")

        params = {
            "address": address,
            "key": secrets.get_secret("GOOGLE_API_KEY"),
        }

        response = requests.get(url, params=params)
        return response.json()["results"][0]["geometry"]["location"]
    except Exception as e:
        logging.error(f"Erro ao criar coletar latitude e longitude: {e}")
        return {"error": "ADDRESS_ERROR"}
