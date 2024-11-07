import requests
import json
import random
import string
import hmac
import hashlib
import uuid
import threading

class TEST:
    def __init__(self):
        self.url = "https://4klrrenoi3.execute-api.eu-west-1.amazonaws.com/dev/manageEmail"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.emails_created = []  
        self.tokens_created = {}  

    def generate_random_email(self):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{random_string}@example.com"

    def generate_hmac_token(self, email, user_id):
        """Génère un token HMAC basé sur l'email et l'ID utilisateur."""
        message = f"{email}{user_id}".encode('utf-8')
        return hmac.new(message, b"secret_key", hashlib.sha256).hexdigest()

    def create_user(self):
        email = self.generate_random_email()
        self.emails_created.append(email)  
        payload = {"email": email}

        if not payload or "email" not in payload:
            print(f"[CREATE] Erreur : le payload est vide ou l'email est manquant pour {email}.")
            return

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            response.raise_for_status()

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    
                    if "message" in response_json and response_json["message"] == "Email already exists":
                        print(f"[CREATE] L'email {email} existe déjà. Voici le token :", response_json["token"])
                        return response_json["token"]
                    
                    user_id = str(uuid.uuid4()) 
                    token = self.generate_hmac_token(email, user_id)
                    
                    put_payload = {"email": email, "user_id": user_id, "token": token}
                    put_response = requests.put(self.url, headers=self.headers, json=put_payload)
                    put_response.raise_for_status()
                    
                    if put_response.status_code == 200:
                        print(f"[CREATE] L'email {email} a été créé avec succès, Token : {token}")
                        self.tokens_created[email] = token 
                        return token
                    else:
                        print(f"[CREATE] Erreur lors de la création de l'utilisateur {email} :", put_response.text)
                except json.JSONDecodeError:
                    print("[CREATE] Erreur : la réponse du serveur n'est pas au format JSON.")
            else:
                print(f"[CREATE] Erreur HTTP : {response.status_code} - {response.text}")

        except requests.exceptions.HTTPError as err:
            print("[CREATE] Erreur HTTP :", err)
        except Exception as e:
            print("[CREATE] Erreur :", e)

    def get_user(self, email):
        if email not in self.tokens_created:
            print(f"[GET] Erreur : aucun token trouvé pour {email}.")
            return

        payload = {"email": email}

        if not payload or "email" not in payload:
            print(f"[GET] Erreur : le payload est vide ou l'email est manquant pour {email}.")
        else:
            try:
                response = requests.post(self.url, headers=self.headers, json=payload)
                response.raise_for_status()

                if response.status_code == 200:
                    try:
                        response_json = response.json()
                        if "token" in response_json:
                            print(f"[GET] Voici le token associé à l'email {email} :", response_json["token"])
                        else:
                            print(f"[GET] L'email {email} n'existe pas dans la base de données.")
                    except json.JSONDecodeError:
                        print("[GET] Erreur : la réponse du serveur n'est pas au format JSON.")
                else:
                    print(f"[GET] Erreur HTTP : {response.status_code} - {response.text}")

            except requests.exceptions.HTTPError as err:
                print("[GET] Erreur HTTP :", err)
            except Exception as e:
                print("[GET] Erreur :", e)

def create_user(test_instance):
    test_instance.create_user()

def get_user(test_instance, email):
    test_instance.get_user(email)

test_instance = TEST()

create_threads = []
for _ in range(3):
    thread = threading.Thread(target=create_user, args=(test_instance,))
    create_threads.append(thread)
    thread.start()

for thread in create_threads:
    thread.join()

get_threads = []
for email in test_instance.emails_created:
    thread = threading.Thread(target=get_user, args=(test_instance, email))
    get_threads.append(thread)
    thread.start()

for thread in get_threads:
    thread.join()

print("Tous les threads ont terminé et tous les utilisateurs ont été vérifiés.")
