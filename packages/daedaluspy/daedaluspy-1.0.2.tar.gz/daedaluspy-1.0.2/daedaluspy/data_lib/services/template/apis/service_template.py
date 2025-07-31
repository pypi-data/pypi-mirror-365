SERVICE_TEMPLATE = """
from typing import Any, Dict, Optional
from dataclasses import dataclass
import requests
from .{service_name_lower}_auth import {service_name}Auth

@dataclass
class {service_name}Service:
    service_auth: {service_name}Auth
    headers: Dict[str, str]
    get_url: str
    post_url: str
    update_url: str
    delete_url: str

    def get_data(self, resource_id: str) -> Dict[str, Any]:
        \"\"\"
        Busca um recurso da API.
        \"\"\"
        response = requests.get(url=self.get_url, headers=self.headers)
        return response

    def post_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Cria um novo recurso na API.
        \"\"\"
        response = requests.post(url=self.post_url, json=data, headers=self.headers)
        return response

    def update_data(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Atualiza um recurso existente na API.
        \"\"\"
        response = requests.put(url=self.update_url, json=data, headers=self.headers)
        return response

    def delete_data(self, resource_id: str) -> None:
        \"\"\"
        Exclui um recurso da API.
        \"\"\"
        response = requests.delete(url=self.delete_url, headers=self.headers)
        return response
"""