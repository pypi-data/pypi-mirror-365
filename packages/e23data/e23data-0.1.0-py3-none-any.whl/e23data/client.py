# e23data_client.py

import requests
from typing import Optional, Dict, List, Any

# URL base da sua API implantada
# Certifique-se de que esta URL está correta e usa HTTPS!
BASE_API_URL = "https://e23data.pyserverbrasil.com.br"

class E23DataClient:
    """
    Cliente Python para interagir com a API de Propriedades Químicas E23Data.
    """
    def __init__(self, base_url: str = BASE_API_URL):
        self.base_url = base_url
        self.properties_url = f"{self.base_url}/properties" # Sem a barra final para flexibilidade

    def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """
        Método interno para fazer requisições HTTP e tratar erros.
        Retorna o JSON da resposta, ou None para 204 No Content/404 Not Found.
        """
        try:
            # Não usamos verify=False aqui em produção, pois a API já tem SSL válido.
            # Se você tiver problemas de certificado em algum ambiente, pode adicionar verify=False,
            # mas é melhor resolver a cadeia de certificados.
            response = requests.request(method, url, **kwargs)
            response.raise_for_status() # Levanta um HTTPError para status 4xx/5xx

            if response.status_code == 204:
                return None
            
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"Erro HTTP ao acessar {url}: {http_err}")
            if http_err.response is not None:
                try:
                    print(f"Detalhes da API: {http_err.response.json()}")
                except requests.exceptions.JSONDecodeError:
                    print(f"Detalhes da API (texto): {http_err.response.text}")
            raise # Re-levanta o erro para a função chamadora
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Erro de conexão: Não foi possível conectar a {url}. Verifique sua conexão e se a API está online.")
            raise
        except requests.exceptions.Timeout as timeout_err:
            print(f"Tempo limite excedido ao acessar {url}. A API pode estar lenta ou inacessível.")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Erro inesperado na requisição para {url}: {req_err}")
            raise

    def get_all_properties(self) -> List[Dict[str, Any]]:
        """Obtém todas as propriedades químicas disponíveis na API."""
        return self._make_request("GET", self.properties_url + "/") # Adiciona barra final para listar

    def get_property_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtém informações completas de uma propriedade pelo nome."""
        try:
            return self._make_request("GET", f"{self.properties_url}/{name}")
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 404:
                print(f"Propriedade '{name}' não encontrada.")
                return None
            raise

    def get_density(self, property_name: str, temperature: float) -> Optional[float]:
        """
        Calcula a densidade de uma propriedade em uma dada temperatura.
        Temperatura deve estar na unidade esperada pelo modelo (e.g., Kelvin).
        """
        url = f"{self.properties_url}/{property_name}/density"
        params = {"temperature": temperature}
        try:
            response_data = self._make_request("GET", url, params=params)
            return response_data.get("density") if response_data else None
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code in [400, 404]:
                print(f"Erro ao obter densidade para '{property_name}': {e.response.json().get('detail', e.response.text)}")
                return None
            raise

    def get_viscosity(self, property_name: str, temperature: float) -> Optional[float]:
        """
        Calcula a viscosidade de uma propriedade em uma dada temperatura.
        Temperatura deve estar na unidade esperada pelo modelo (e.g., Kelvin).
        """
        url = f"{self.properties_url}/{property_name}/viscosity"
        params = {"temperature": temperature}
        try:
            response_data = self._make_request("GET", url, params=params)
            return response_data.get("viscosity") if response_data else None
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code in [400, 404]:
                print(f"Erro ao obter viscosidade para '{property_name}': {e.response.json().get('detail', e.response.text)}")
                return None
            raise

    # Você pode adicionar métodos para criar, atualizar e deletar propriedades aqui também
    # def create_property(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     return self._make_request("POST", self.properties_url + "/", json=data)

    # def update_property(self, prop_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    #     return self._make_request("PUT", f"{self.properties_url}/{prop_id}", json=data)

    # def delete_property(self, prop_id: int):
    #     self._make_request("DELETE", f"{self.properties_url}/{prop_id}")


# Exemplo de uso direto das funções (como você quer no Colab)
_client = E23DataClient()

def get_density(property_name: str, temperature: float) -> Optional[float]:
    """Wrapper para E23DataClient.get_density."""
    return _client.get_density(property_name, temperature)

def get_viscosity(property_name: str, temperature: float) -> Optional[float]:
    """Wrapper para E23DataClient.get_viscosity."""
    return _client.get_viscosity(property_name, temperature)

def get_all_properties() -> List[Dict[str, Any]]:
    """Wrapper para E23DataClient.get_all_properties."""
    return _client.get_all_properties()

def get_property_info(property_name: str) -> Optional[Dict[str, Any]]:
    """Wrapper para E23DataClient.get_property_info."""
    return _client.get_property_info(property_name)


if __name__ == "__main__":
    print("Testando a biblioteca cliente localmente...")

    # Teste de densidade
    temp_kelvin = 298.15 # 25°C em Kelvin
    density_water = get_density("Water", temperature=temp_kelvin)
    if density_water is not None:
        print(f"Densidade da Água a {temp_kelvin} K: {density_water:.4f} kg/m³")
    else:
        print("Não foi possível obter a densidade da Água.")

    density_ethanol = get_density("Ethanol", temperature=temp_kelvin)
    if density_ethanol is not None:
        print(f"Densidade do Etanol a {temp_kelvin} K: {density_ethanol:.4f} kg/m³")
    else:
        print("Não foi possível obter a densidade do Etanol.")

    # Teste de viscosidade
    viscosity_methane = get_viscosity("Methane", temperature=150.0)
    if viscosity_methane is not None:
        print(f"Viscosidade do Metano a 150 K: {viscosity_methane:.8f} Pa.s")
    else:
        print("Não foi possível obter a viscosidade do Metano.")

    # Teste de propriedade inexistente
    density_non_existent = get_density("Acetone", temperature=300.0)
    if density_non_existent is None:
        print("Teste de propriedade inexistente: Acetone (conforme esperado, retornou None).")

    # Listar todas as propriedades
    print("\n--- Listando todas as propriedades ---")
    all_props = get_all_properties()
    if all_props:
        for prop in all_props:
            print(f"- {prop['name']}")
    else:
        print("Nenhuma propriedade encontrada.")

    # Obter info completa de uma propriedade
    print("\n--- Obtendo info completa de Water ---")
    water_info = get_property_info("Water")
    if water_info:
        print(water_info)
    else:
        print("Não foi possível obter info de Water.")