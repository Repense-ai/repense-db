import logging
import json
import requests
import os

from repensedb.connections.firebase import FirebaseConnection
from repensedb.utils.logs import LOGGING_CONFIG


logging.basicConfig(**LOGGING_CONFIG)


class FirebaseAuth:
    def __init__(self, connection: FirebaseConnection):
        """
        Initialize Firebase Auth with a Firebase connection

        Args:
            connection: A FirebaseConnection instance
        """
        if not isinstance(connection, FirebaseConnection):
            raise TypeError("Connection must be a FirebaseConnection instance")

        if not connection.is_connected():
            connection.connect()

        self.connection = connection
        self.auth = connection.auth

    @staticmethod
    def validate_password(error_string: str):
        try:
            error_check = {
                "lower case": False,
                "upper case": False,
                "6 characters": False,
                "20 characters": False,
                "non-alphanumeric": False,
                "numeric": False,
                "EMAIL_EXISTS": False,
                "PHONE_EXISTS": False,
            }

            for key in error_check:
                if key.lower() in error_string.lower():
                    error_check[key] = True

            return error_check
        except Exception:
            return error_string

    def sign_up(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: str,
    ):
        try:
            user = self.auth.create_user(
                email=email,
                password=password,
                display_name=f"{first_name} {last_name}",
                phone_number=phone,
            )

            logging.info(f"User {email} created successfully.")
            return user

        except self.auth.EmailAlreadyExistsError:
            error_check = self.validate_password("EMAIL_EXISTS")
            logging.error("Error creating user: email already exists.")
            return error_check
        except self.auth.PhoneNumberAlreadyExistsError:
            error_check = self.validate_password("PHONE_EXISTS")
            logging.error("Error creating user: phone number already exists.")
            return error_check
        except Exception as e:
            error_check = self.validate_password(str(e))
            logging.error(f"Error creating user: {e}")
            return error_check

    def sign_in(self, email: str, password: str):
        try:
            api_key = self.connection.config.get("api_key") or os.getenv(
                "FIREBASE_WEB_API_KEY"
            )
            if not api_key:
                raise ValueError("Firebase Web API key not found")

            url = "https://identitytoolkit.googleapis.com"
            endpoint = f"v1/accounts:signInWithPassword?key={api_key}"
            sign_in_url = f"{url}/{endpoint}"

            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True,
            }

            response = requests.post(sign_in_url, json=payload)

            if response.status_code == 200:
                user_data = response.json()
                logging.info(f"User {email} signed in successfully.")
                return user_data
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get(
                    "message", "Unknown error"
                )
                logging.error(f"Sign in failed: {error_message}")
                return {"error": error_message}

        except Exception as e:
            logging.error(f"Error during sign in: {e}")
            return {"error": str(e)}

    def refresh_id_token(self, refresh_token: str):
        try:
            api_key = self.connection.config.get("api_key") or os.getenv(
                "FIREBASE_WEB_API_KEY"
            )
            if not api_key:
                raise ValueError("Firebase Web API key not found")

            url = "https://securetoken.googleapis.com/v1/token"
            params = {"key": api_key}
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }

            response = requests.post(url, params=params, data=payload)

            if response.status_code == 200:
                new_tokens = response.json()
                logging.info("ID token refreshed successfully.")
                return new_tokens
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get(
                    "message", "Unknown error"
                )
                logging.error(f"Token refresh failed: {error_message}")
                return {"error": error_message}

        except Exception as e:
            logging.error(f"Error during token refresh: {e}")
            return {"error": str(e)}

    def verify_id_token(self, id_token: str):
        try:
            decoded_token = self.auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logging.error(f"Error verifying ID token: {e}")
            return {"error": str(e)}

    def send_email_verification(self, id_token: str):
        try:
            api_key = self.connection.config.get("api_key") or os.getenv(
                "FIREBASE_WEB_API_KEY"
            )
            if not api_key:
                raise ValueError("Firebase Web API key not found")

            url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode"
            params = {"key": api_key}
            headers = {"content-type": "application/json; charset=UTF-8"}
            data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})

            response = requests.post(url, headers=headers, params=params, data=data)
            return response.json()
        except Exception as e:
            logging.error(f"Error sending email verification: {e}")
            return None

    def send_password_reset_email(self, email: str):
        try:
            api_key = self.connection.config.get("api_key") or os.getenv(
                "FIREBASE_WEB_API_KEY"
            )
            if not api_key:
                raise ValueError("Firebase Web API key not found")

            url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode"
            params = {"key": api_key}
            headers = {"content-type": "application/json; charset=UTF-8"}
            data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})

            response = requests.post(url, headers=headers, params=params, data=data)
            return response.json()
        except Exception as e:
            logging.error(f"Error sending password reset email: {e}")
            return None

    def get_email_link(self, email: str):
        try:
            link = self.auth.generate_email_verification_link(email)
            return {"verificationLink": link}
        except Exception as e:
            logging.error(f"Error generating email verification link: {e}")
            return None

    def get_reset_link(self, email: str):
        try:
            link = self.auth.generate_password_reset_link(email)
            return {"resetLink": link}
        except Exception as e:
            logging.error(f"Error generating password reset link: {e}")
            return None

    def get_user_info(self, uid: str):
        try:
            user = self.auth.get_user(uid)
            return user
        except Exception as e:
            logging.error(f"Error getting user info: {e}")
            return None

    def delete_user(self, uid: str):
        try:
            self.auth.delete_user(uid)
            logging.info("User deleted successfully.")
            return True
        except Exception as e:
            logging.error(f"Error deleting user: {e}")
            raise e
