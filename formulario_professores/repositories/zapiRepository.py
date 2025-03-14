import requests
from django.conf import settings

class ZapiRepository:
    @staticmethod
    def criar_instancia(name):
        url = "https://api.z-api.io/instances/integrator/on-demand"
        bearer_token = settings.ZAPI_PARTNER_TOKEN

        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": name  # Ajuste os dados conforme o esperado pela API
        }

        try:
            response = requests.post(url, headers=headers, json=data)

            # Verificando o status e a resposta
            if response.status_code == 200:
                print("Requisição bem-sucedida!")
                return response.json()  # Retorna a resposta JSON caso seja sucesso
            else:
                print(f"Erro: {response.status_code}")
                print(response.text)
                return {"status": "error", "message": response.text}  # Retorna erro com a mensagem da resposta

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {str(e)}")
            return {"status": "error", "message": str(e)}  # Retorna erro caso ocorra alguma exceção
        
    @staticmethod
    def get_qrcode(instancia, token):
        url = f"https://api.z-api.io/instances/{instancia}/token/{token}/qr-code/image"
        bearer_token = settings.ZAPI_CLIENT_TOKEN


        headers = {
            "Client-Token": bearer_token,
        }

        try:
            response = requests.get(url, headers=headers)

            # Verificando o status e a respost
            if response.status_code == 200:
                result = response.json()
                if result:
                    return result  # Retorna a string base64 da imagem
                else:
                    return {"status": "error", "message": result.get("message", "Erro desconhecido.")}

            else:
                return {"status": "error", "message": response.text}  # Retorna erro com a mensagem da resposta

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}  # Retorna erro caso ocorra alguma exceçã

    @staticmethod
    def get_status(instancia, token):
        url = f"https://api.z-api.io/instances/{instancia}/token/{token}/status"
        bearer_token = settings.ZAPI_CLIENT_TOKEN


        headers = {
            "Client-Token": bearer_token,
        }

        try:
            response = requests.get(url, headers=headers)

            # Verificando o status e a respost
            if response.status_code == 200:
                result = response.json()
                if result:
                    return result  # Retorna a string base64 da imagem
                else:
                    return {"status": "error", "message": result.get("message", "Erro desconhecido.")}

            else:
                return {"status": "error", "message": response.text}  # Retorna erro com a mensagem da resposta

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}  # Retorna erro caso ocorra alguma exceçã
        
    @staticmethod
    def desconectar(instancia, token):
        url = f"https://api.z-api.io/instances/{instancia}/token/{token}/disconnect"
        bearer_token = settings.ZAPI_CLIENT_TOKEN


        headers = {
            "Client-Token": bearer_token,
        }

        try:
            response = requests.get(url, headers=headers)

            # Verificando o status e a respost
            if response.status_code == 200:
                result = response.json()
                if result:
                    return result  # Retorna a string base64 da imagem
                else:
                    return {"status": "error", "message": result.get("message", "Erro desconhecido.")}

            else:
                return {"status": "error", "message": response.text}  # Retorna erro com a mensagem da resposta

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}  # Retorna erro caso ocorra alguma exceçã



