import requests
import argparse

# argumento para o host
hostParser = argparse.ArgumentParser()
hostParser.add_argument("--host", type=str)
hostParser.add_argument("--users", type=int)
host = hostParser.parse_args()

def http_requests():
    
    # criação de usuário
    payload = {
        'email': f'user{i}@teste.com',
        'password': 'teste'
        }

    response = requests.post(f"http://{host.host}:8080/users", json=payload)

    if response.status_code == 201: #caso a criação de usuário seja bem-sucedida, será efetuado o login
        data = {
            'username': '',
            'password': ''
        }
        data['username'] = payload['email']
        data['password'] = payload['password']
        #comando de login
        response = requests.post(f"http://{host.host}:8080/token", data)

        #obtenção de token de autenticação
        token_data = response.json()
        token = token_data.get('access_token')
        token_type = token_data.get('token_type')

        #dicionário para cabeçalho da requisição    
        headers = {
            'Authorization': f'{token_type.capitalize()} {token}'
        }
        link = {
            'original_url': 'https://www.linkedin.com/in/weslei-santos-826b70167/'
        }

        #criação do link
        response = requests.post(f"http://{host.host}:8080/links", json=link, headers=headers)
        print(response.status_code)

for i in range(host.users):
    http_requests()
