AUTH_TEMPLATE = """
from dataclasses import dataclass, field
from typing import Dict, Optional
import requests

@dataclass
class {service_name}Auth:
    credentials: Dict[str, str]
    auth_url: str
    auth_headers: Dict[str, str]
    auth_token: Optional[str] = field(default=None)

    def get_access(self) -> str:
        \"\"\"
        Obtém o token de acesso da API.
        \"\"\"
        response = requests.post(url=self.auth_url, data=self.credentials.get('auth_data'), headers=self.auth_headers)

    def refresh_access(self) -> str:
        \"\"\"
        Lógica para renovar o token de acesso.
        \"\"\"
        # Dependendo da API, implemente refresh usando refresh_token ou similar
        return self.get_access()

    def logout(self) -> None:
        \"\"\"
        Lógica para revogar ou encerrar o token de acesso.
        \"\"\"
        # Implemente se a API oferecer endpoint de logout
        pass
"""