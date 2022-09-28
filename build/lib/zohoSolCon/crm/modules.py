import requests
import json



def make_header(token):
	return {
		'Authorization': f'Zoho-oauthtoken {token.access}'
		
	}


def get_modules(token):
	url = 'https://www.zohoapis.com/crm/v3/settings/modules'
	headers = make_header(token)

	response = requests.get(url=url, headers=headers)
	if response.status_code >= 400 and response.status_code < 500:
		token.generate()
		return get_modules()
	else:
		content = json.loads(response.content.decode('utf-8'))
		modules = content.get("modules")
		return token, modules

