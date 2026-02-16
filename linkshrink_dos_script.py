import requests
import argparse
import string
import random
from concurrent.futures import ThreadPoolExecutor

# host argument
hostParser = argparse.ArgumentParser()
hostParser.add_argument("--host", type=str)
hostParser.add_argument("--users", type=int)
hostParser.add_argument("--threads", type=int, default=100)
hostParser.add_argument("--protocol", type=str, default="https")
host = hostParser.parse_args()

def http_requests(i):
    # user creation
    payload = {
      'email': f"{''.join(random.SystemRandom().choices(string.ascii_letters, k=512))}@{''.join(random.SystemRandom().choices(string.ascii_letters, k=512))}.com",
      'password': ''.join(random.SystemRandom().choices(string.ascii_letters, k=1024))
    }


    headers = {
      'Accept': '*/*',
      'Accept-Encoding': 'gzip, deflate, br, zstd',
      'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
      'Connection': 'keep-alive',
      'Content-Length': '47',
      'Content-Type': 'application/json',
      'DNT': '1',
      'Host': f'{host.host}',
      'Origin': f'{host.protocol}://{host.host}',
      'Referer': f'{host.protocol}://{host.host}/login',
      'Sec-Fetch-Dest': 'empty',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-origin',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
      'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Linux"'
    }

    response = requests.post(f"{host.protocol}://{host.host}/users", json=payload, headers=headers)

    print(f'user creation status code: {response.status_code}')

    # effect login in case of the user creation was successful
    if response.status_code == 201:  
      data = {
        'username': payload['email'],
        'password': payload['password']
      }
     # login comand
      response = requests.post(f"{host.protocol}://{host.host}/token", data, headers=headers)
     # get token to authentication
      token_data = response.json()
      token = token_data.get('access_token')
      token_type = token_data.get('token_type')

     # new header to authentication    
      auth_header = {
          'Authorization': f'{token_type.capitalize()} {token}'
      }
      headers.update(auth_header)
      link = {
          'original_url': 'https://www.linkedin.com/in/weslei-santos-826b70167/'
      }
     # link creation
      response = requests.post(f"{host.protocol}://{host.host}/links", json=link, headers=headers)
      print(f"link creation status code: {response.status_code}")

# multithread implementation
if __name__ == "__main__":
    print(f"Iniciando {host.users} requisições com {host.threads} threads simultâneas...")
    
    with ThreadPoolExecutor(max_workers=host.threads) as executor:
        executor.map(http_requests, range(host.users))