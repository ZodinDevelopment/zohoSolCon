import requests
import json

BASEURL = 'https://projectsapi.zoho.com/restapi'


def make_header(token):
    return {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }


def get_projects(token, portal_id, **kwargs):
    url = BASEURL + f'/portal/{portal_id}/projects/'
    headers = make_header(token)

    response = requests.get(url=url, headers=headers, params=kwargs)

    if response.status_code == 401:
        token.generate()
        return get_projects(token, portal_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("projects")


def get_project(token, portal_id, project_id):
    url = BASEURL + f'/portal/{portal_id}/projects/{project_id}/'
    headers = make_header(token)

    response = requests.get(url=url, headers=headers)

    if response.status_code == 401:
        token.generate()
        return get_project(token, portal_id, project_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        project = content['projects'][0]
        return token, project



