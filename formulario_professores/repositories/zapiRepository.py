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
        
    @staticmethod
    def enviar_mensagem(id_instancia, token_instancia, client_token, contato, mensagem):

        zapi_url = f"https://api.z-api.io/instances/{id_instancia}/token/{token_instancia}/send-text"
    
        # Conteúdo da mensagem a ser enviada
        payload = {
            "phone": contato,
            "message": f"{mensagem}"
        }

        # Fazer a requisição POST para a API da Z-API
        try:
            response = requests.post(zapi_url, json=payload, headers={'Content-Type': "application/json", 'Client-Token': client_token})
            response.raise_for_status()  # Levanta uma exceção para status HTTP >= 400
            return response.json()  # Retorna a resposta da API se tudo ocorrer bem
        except requests.RequestException as e:
            print(f"Erro ao enviar a mensagem para o WhatsApp: {e}")
            return None

    @staticmethod
    def enviar_imagem(id_instancia, token_instancia, client_token, contato, imagem):

        zapi_url = f"https://api.z-api.io/instances/{id_instancia}/token/{token_instancia}/send-image"
    
        # Conteúdo da mensagem a ser enviada
        payload = {
            "phone": contato,
            "image": f"{imagem}"
        }

        # Fazer a requisição POST para a API da Z-API
        try:
            response = requests.post(zapi_url, json=payload, headers={'Content-Type': "application/json", 'Client-Token': client_token})
            response.raise_for_status()  # Levanta uma exceção para status HTTP >= 400
            return response.json()  # Retorna a resposta da API se tudo ocorrer bem
        except requests.RequestException as e:
            print(f"Erro ao enviar a imagem para o WhatsApp: {e}")
            return None
        
    @staticmethod
    def enviar_audio(id_instancia, token_instancia, client_token, contato, audio):

        zapi_url = f"https://api.z-api.io/instances/{id_instancia}/token/{token_instancia}/send-audio"
    
        # Conteúdo da mensagem a ser enviada
        payload = {
            "phone": contato,
            "audio": f"{audio}"
        }

        # Fazer a requisição POST para a API da Z-API
        try:
            response = requests.post(zapi_url, json=payload, headers={'Content-Type': "application/json", 'Client-Token': client_token})
            response.raise_for_status()  # Levanta uma exceção para status HTTP >= 400
            return response.json()  # Retorna a resposta da API se tudo ocorrer bem
        except requests.RequestException as e:
            print(f"Erro ao enviar a imagem para o WhatsApp: {e}")
            return None


    @staticmethod
    def enviar_video(id_instancia, token_instancia, client_token, contato, video):

        zapi_url = f"https://api.z-api.io/instances/{id_instancia}/token/{token_instancia}/send-video"
    
        # Conteúdo da mensagem a ser enviada
        payload = {
            "phone": contato,
            "video": f"{video}"
        }

        # Fazer a requisição POST para a API da Z-API
        try:
            response = requests.post(zapi_url, json=payload, headers={'Content-Type': "application/json", 'Client-Token': client_token})
            response.raise_for_status()  # Levanta uma exceção para status HTTP >= 400
            return response.json()  # Retorna a resposta da API se tudo ocorrer bem
        except requests.RequestException as e:
            print(f"Erro ao enviar a imagem para o WhatsApp: {e}")
            return None


