import requests
from requests import HTTPError
from requests import Session
import threading

class TEST():
    def __init__(self, token):
        self.session = Session()
        self.session.headers = {
            'x-api-key': token
        }
        self.base_url = 'https://4klrrenoi3.execute-api.eu-west-1.amazonaws.com/dev'

    def get_user(self):
        try:
            res = self.session.get(
                url=f"{self.base_url}/manageUser"
            )
            res.raise_for_status()
            
            print(f"Response Status Code: {res.status_code}")
            
            email = res.text.strip()  
            
            if email:
                print(f"Email trouvé : {email}")
            else:
                print("L'email n'a pas été trouvé dans la réponse.")

        except HTTPError as http_err:
            print(f"Erreur HTTP : {http_err}")
            print(f"Réponse : {http_err.response.text}")
        except Exception as err:
            print(f"Autre erreur : {err}")

tokens = [
    'ac46153c6444f069e6a1059e70d91ee7193d1b2177e236f736d681a6baf55f2d',
    '4b88aa3efb9f1235f9512d0bcb12e9e37951981b2397c358c68c0253c539d4ec',
    'c1363b8c7756180fe041d21e01a05aa51cc6f11125bf1a9801ea7a5032408478'
]

def test_token(token):
    test_instance = TEST(token)
    test_instance.get_user()

threads = []

for token in tokens:
    thread = threading.Thread(target=test_token, args=(token,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("Tous les tests avec les tokens ont été effectués.")
