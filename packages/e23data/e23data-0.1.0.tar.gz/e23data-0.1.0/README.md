    # E23Data Python Client Library

    Esta biblioteca fornece um cliente Python simples para interagir com a API de Propriedades Químicas E23Data. Ela permite aos usuários consultar e calcular facilmente propriedades químicas como densidade e viscosidade com base na temperatura.

    ## Instalação

    Você pode instalar a biblioteca `e23data` usando pip:

    ```bash
    pip install e23data
    ```

    ## Uso

    Veja como você pode usar a biblioteca em seus projetos Python ou em ambientes como o Google Colab:

    ```python
    from e23data import get_density, get_viscosity, get_all_properties, get_property_info

    # Calcular densidade da Água a 298.15 Kelvin (25°C)
    density_water = get_density("Water", temperature=298.15)
    if density_water is not None:
        print(f"Densidade da Água a 298.15 K: {density_water:.4f} kg/m³")

    # Calcular viscosidade do Metano a 150 Kelvin
    viscosity_methane = get_viscosity("Methane", temperature=150.0)
    if viscosity_methane is not None:
        print(f"Viscosidade do Metano a 150 K: {viscosity_methane:.8f} Pa.s")

    # Obter todas as propriedades disponíveis
    print("\nTodas as Propriedades:")
    all_props = get_all_properties()
    if all_props:
        for prop in all_props:
            print(f"- {prop.get('name')}")

    # Obter informações completas para uma propriedade específica
    print("\nInformações para Etanol:")
    ethanol_info = get_property_info("Ethanol")
    if ethanol_info:
        print(ethanol_info)
    ```

    ## API Endpoint

    Esta biblioteca cliente interage com a API de Propriedades Químicas E23Data, hospedada em: `https://e23data.pyserverbrasil.com.br`

    Você pode encontrar a documentação interativa da API (Swagger UI) em: `https://e23data.pyserverbrasil.com.br/docs`

    ## Desenvolvimento

    ### Testando a Biblioteca Cliente Localmente

    Para testar a biblioteca cliente contra sua API implantada (ou uma instância local da API):

    1.  **Certifique-se de que sua API E23Data esteja em execução e acessível** (localmente em `http://127.0.0.1:8000` ou publicamente em `https://e23data.pyserverbrasil.com.br`).
    2.  **Navegue até o diretório raiz deste projeto da biblioteca cliente.**
    3.  **Execute o arquivo `client.py`:**
        ```bash
        python3 src/e23data/client.py
        ```
        Isso executará os testes de exemplo definidos no script.

    ## Licença

    Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
    ```
