import requests
from tqdm import tqdm

# Função principal para obter alertas e políticas
def get_alerts_and_policies(api_key):
    headers = {
        "Api-Key": api_key
    }

    # Dicionário para mapear os paths aos seus nomes legíveis
    path_names = {
        "nrql_conditions": "NRQL Condition",  # Condições NRQL
        "conditions": "APM/Browser/Mobile Condition",  # Condições APM/Navegador/Mobile
        "external_service_conditions": "External Services Condition",  # Condições de Serviços Externos
        "synthetics_conditions": "Synthetic Monitoring Condition",  # Condições de Monitoramento Sintético
        "infra_conditions": "Infrastructure Condition"  # Condições de Infraestrutura
    }

    # Função para obter informações detalhadas de um alerta por ID
    def get_alert_by_id(alert_id):
        alert_url = f"https://api.newrelic.com/v2/alerts_conditions/{alert_id}.json"
        alert_response = requests.get(alert_url, headers=headers)

        if alert_response.status_code != 200:
            print(f"Falha ao obter alerta com ID: {alert_id}.")  # Mensagem de falha ao obter alerta
            return None

        alert_data = alert_response.json().get("data", {})
        return alert_data

    # Chamada à API para obter a lista de políticas
    policies_url = "https://api.newrelic.com/v2/alerts_policies.json"
    policies_response = requests.get(policies_url, headers=headers)

    # Verificar se a solicitação foi bem-sucedida
    if policies_response.status_code != 200:
        print("Falha ao obter lista de políticas.")  # Mensagem de falha ao obter lista de políticas
        return

    policies_data = policies_response.json()["policies"]

    # Contar o total de políticas para a barra de progresso
    total_policies = len(policies_data)
    # Criar a barra de progresso
    progress_bar = tqdm(total=total_policies, desc="Políticas Processadas", unit="política")

    # Abrir o arquivo para escrita (modo 'w')
    with open("Alertas.txt", "w") as file:
        # Agora, para cada política, obtemos a lista de alertas associados a ela
        for policy in policies_data:
            policy_id = policy["id"]
            policy_name = policy["name"]
            file.write(f"ID da Política: {policy_id} - Política: {policy_name}\n")

            # Função auxiliar para obter alertas de um determinado tipo de path
            def get_alerts_by_path(path_type, path_name):
                page = 1
                limit = 50
                while True:
                    alerts_url = f"https://api.newrelic.com/v2/alerts_{path_type}.json?policy_id={policy_id}&page={page}&limit={limit}"
                    alerts_response = requests.get(alerts_url, headers=headers)

                    if alerts_response.status_code != 200:
                        file.write(f"  Falha ao obter alertas do path {path_name} para a política {policy_id}.\n")
                        break

                    alerts_data = alerts_response.json().get(path_type, [])
                    if not alerts_data:
                        break

                    # Processar cada alerta
                    for alert in alerts_data:
                        alert_id = alert["id"]
                        alert_status = "Ativo" if alert["enabled"] else "Inativo"
                        file.write(f"  Tipo de Alerta: {path_name} - Nome do Alerta: {alert['name']} "
                                   f"- ID do Alerta: {alert_id} - Status: {alert_status}\n")

                    page += 1  # Avançar para a próxima página

            # Processar alertas para cada tipo de caminho
            for path_type, path_name in path_names.items():
                if path_type == "infra_conditions":
                    infra_conditions = get_infrastructure_conditions(api_key, policy_id)
                    for condition in infra_conditions:
                        alert_id = condition["id"]
                        alert_status = "Ativo" if condition["enabled"] else "Inativo"
                        file.write(f"  Tipo de Alerta: {path_name} - Nome do Alerta: {condition['name']} "
                                   f"- ID do Alerta: {alert_id} - Status: {alert_status}\n")
                else:
                    get_alerts_by_path(path_type, path_name)

            # Pular uma linha para a próxima política
            file.write("\n")

            # Atualizar a barra de progresso
            progress_bar.update(1)

    # Fechar a barra de progresso ao concluir
    progress_bar.close()

# Função para obter as condições de infraestrutura
def get_infrastructure_conditions(api_key, policy_id):
    headers = {
        "Api-Key": api_key
    }

    conditions_url = f"https://infra-api.newrelic.com/v2/alerts/conditions?policy_id={policy_id}"
    response = requests.get(conditions_url, headers=headers)

    if response.status_code != 200:
        print(f"Falha ao obter condições de infraestrutura para a política {policy_id}.")  # Mensagem de falha ao obter condições de infraestrutura
        return []

    conditions_data = response.json().get("data", [])
    return conditions_data

# Verificar se o script está sendo executado diretamente
if __name__ == "__main__":
    api_key = "XXX-YYY-XXX"  # Substitua pelo seu próprio API key
    get_alerts_and_policies(api_key)

# 
# MIT License
#
# Copyright (c) [2024] [Street-Dog]
# https://github.com/StreetDogBR
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
