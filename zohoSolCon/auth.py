import time
import requests
import json
import os
from datetime import datetime
import pickle


class Token:
    def __init__(self, client_id, client_secret, grant_token=None, refresh_token=None, save_refresh=True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access = None
        self.refresh = refresh_token
       # self.init_token_dir()
        if refresh_token is not None:
        	self.generate()
        if grant_token is not None:
            self.access, self.refresh = self._authorize(grant_token)
        if save_refresh:
        	self.write_to_file("token.pkl")
        
    def _authorize(self, grant_token):
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            "grant_type":"authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": grant_token
        }
        
        response = requests.post(url=url, data=data)
        print(response.status_code)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            print(content)
            access_token = content.get("access_token")
            refresh_token = content.get("refresh_token")
            self.auth_time = datetime.utcnow()
            self.valid_for = content.get("expires_in")
            return access_token, refresh_token
        else:
            raise Exception("Need to build exceptions")

    def init_token_dir(self):
        self.token_path = os.path.join("~", "ZohoOauthVault")
        if not os.path.exists(self.token_path):
            os.mkdir(self.token_path)

        else:
            dir_contents = os.listdir(self.token_path)
            print(f"A directory has already been setup previously, {len(dir_contens)} refresh tokens were found.")
            token_prompt = str(input("Would you like to use an already existing token? [y/N] --> "))
            answer = token_prompt.strip().upper()
            if answer == "N":
                return

            elif answer == "Y":
                os.system('clear')
                for idx, file in enumerate(dir_contents):
                    print(f'[{idx}] {file}')

                try:
                    token_select = int(input("Use the numerical keys to select a token to use --> "))
                    self.token_path = os.path.join(self.token_path, dir_contents[0])
                except TypeError:
                    print("Error: expected integer response.")
                    time.sleep(3)
                    os.system('clear')
                  #  return self.init_token_dir()
               # try:
                    #token = dir_contents[token_select]


    def _generate(self):
        url = "https://accounts.zoho.com/oauth/v2/token?refresh_token={}".format(self.refresh)
        url += "&client_id={}".format(self.client_id)
        url += "&client_secret={}".format(self.client_secret)
        url += "&grant_type=refresh_token"
	     
        response = requests.post(url=url)
        if response.status_code == 200:
            content = json.loads(response.content.decode('utf-8'))
            access_token = content.get("access_token")
            self.valid_for = content.get("expires_in")
            self.auth_time = datetime.utcnow()
            return access_token

       
    def write_to_env(self):
        os.environ["ZOHO_REFRESH_KEY"] = self.refresh

    def read_from_env(self):
        self.refresh = os.environ["ZOHO_REFRESH_KEY"]

    def write_to_file(self, filename="zohotoken.pkl"):
        data_object = {
	    "client_id": self.client_id,
	    "client_secret": self.client_secret,
	    "refresh_token": self.refresh
	}
        with open(filename, 'wb') as handle:
            pickle.dump(data_object, handle, protocol=pickle.HIGHEST_PROTOCOL)
	

    def generate(self):
        self.access = self._generate()
        self.write_to_file()   
    		
    @classmethod
    def from_file(cls, filename):
        try:
            with open(filename, 'rb') as handle:
                data_object = pickle.load(handle)
                client_id = data_object['client_id']
                client_secret = data_object['client_secret']
                refresh = data_object['refresh_token']
            return Token(client_id, client_secret, grant_token=None, refresh_token=refresh)
        except FileNotFoundError:
            print("Invalid Filename")
		
        except KeyError as e:
            print(str(e))
		
					
    
    @property
    def expires_in(self):
        now = datetime.utcnow()
        timedelta = now - self.auth_time

        seconds_in_use = int(timedelta.total_seconds())

        if seconds_in_use <= self.valid_for:
            return self.valid_for - seconds_in_use

        else:
            return None

    
            

        
        
        
