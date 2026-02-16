import requests
import argparse
import string
import random
from concurrent.futures import ThreadPoolExecutor

# argumento para o host
hostParser = argparse.ArgumentParser()
hostParser.add_argument("--host", type=str)
hostParser.add_argument("--users", type=int)
host = hostParser.parse_args()

def http_requests(i):
    """MANTIVE SUA FUNÇÃO EXATAMENTE COMO ESTAVA"""
    # criação de usuário
    payload = {
        'email': f"{''.join(random.SystemRandom().choices(string.ascii_letters, k=512))}@{''.join(random.SystemRandom().choices(string.ascii_letters, k=512))}.com",
        'password': ''.join(random.SystemRandom().choices(string.ascii_letters, k=1024)),
    }

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '47',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Host': 'localhost:8080',
        'Origin': 'http://localhost:8080',
        'Referer': 'http://localhost:8080/login',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    response = requests.post(f"http://{host.host}/users", json=payload, headers=headers)

    if response.status_code == 201: #caso a criação de usuário seja bem-sucedida, será efetuado o login
        data = {
            'username': payload['email'],
            'password': payload['password']
        }
        
        #comando de login
        response = requests.post(f"http://{host.host}/token", data)

        #obtenção de token de autenticação
        token_data = response.json()
        token = token_data.get('access_token')
        token_type = token_data.get('token_type')

        #dicionário para cabeçalho da requisição    
        auth_header = {
            'Authorization': f'{token_type.capitalize()} {token}'
        }

        headers.update(auth_header)
        
        link = {
            'original_url': 'https://www.linkedin.com/in/weslei-santos-826b70167/'
        }

        #criação do link
        response = requests.post(f"http://{host.host}/links", json=link, headers=headers)
        print(response.status_code)

# APENAS ADICIONE ESTAS LINHAS PARA PARALELISMO
if __name__ == "__main__":
    # Substitua o loop sequencial por execução paralela
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Isso executa as requisições em paralelo em vez de sequencial
        executor.map(http_requests, range(host.users))