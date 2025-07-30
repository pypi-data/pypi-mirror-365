"""This module handles HTTP requests and responses to and from the CMS."""

import json
from dataclasses import dataclass
from datetime import datetime

import jwt
from google.cloud import secretmanager


@dataclass
class Secret:
    private_key: str
    kid: str
    principal_key: str


class SecretManagerError(Exception): ...


class GoogleSecretManagerClient:
    TYPE = "JWT"
    ALGORITHM = "RS256"
    _gc_secret_resource_name: str

    def __init__(self, gc_secret_resource_name: str) -> None:
        self._gc_secret_resource_name = gc_secret_resource_name

    def _get_secret(self) -> Secret:
        """Fetches the private key and related data from Google Cloud Secret Manager."""
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(name=self._gc_secret_resource_name)
        raw_data = response.payload.data.decode("UTF-8")
        data = json.loads(raw_data)
        try:
            return Secret(
                private_key=data["privateKey"],
                kid=data["kid"],
                principal_key=data["principalKey"],
            )
        except KeyError as e:
            raise SecretManagerError(
                "The secret must be a JSON object with keys 'privateKey', 'kid' and 'principalKey'."
            ) from e

    def generate_token(self) -> str:
        secret = self._get_secret()

        header = {
            "kid": secret.kid,
            "typ": self.TYPE,
            "alg": self.ALGORITHM,
        }

        iat = int(datetime.now().timestamp())
        exp = iat + 30
        payload = {
            "sub": secret.principal_key,
            "iat": iat,
            "exp": exp,
        }

        token = jwt.encode(
            payload, secret.private_key, algorithm=self.ALGORITHM, headers=header
        )
        return token
