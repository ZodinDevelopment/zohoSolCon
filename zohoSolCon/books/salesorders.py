import requests
import json


def make_header(token):
    return {
        'Authorization': f'Zoho-oauthtoken {token.access}'
    }



def create_salesorder(token, org_id, customer_id, data_object):
    url = 'https://books.zoho.com/api/v3/salesorders'
    headers = make_header(token)
    params = {'organization_id': org_id}

    data_object['customer_id'] = customer_id
    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, params=params, data=data)

    if response.status_code == 401:
        token.generate()
        return create_salesorder(token, org_id, customer_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("message"), content.get("salesorder")


def get_salesorders(token, org_id, **kwargs):
    url = 'htps://books.zoho.com/api/v3/salesorders'
    headers = make_header(token)
    params = kwargs
    params['organization_id'] = org_id

    response = requests.get(url=url, headers=headers, params=params)

    if response.status_code == 401:
        token.generate()
        return get_salesorders(token, org_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("salesorders")


def update_salesorder(token, org_id, salesorder_id, customer_id, data_object):
    url = f'https://books.zoho.com/api/v3/salesorders/{salesorder_id}'
    headers = make_header(token)
    params = {'organization_id': org_id}

    data_object['customer_id'] = customer_id
    data = json.dumps(data_object).encode('utf-8')

    response = requests.put(url=url, headers=headers, params=params, data=data)

    if response.status_code == 401:
        token.generate()
        return update_salesorder(token, org_id, salesorder_id, customer_id, data_object)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('messsage'), content.get("salesorder")


def get_salesorder(token, org_id, salesorder_id, **kwargs):
    url = f'https://books.zoho.com/api/v3/salesorders/{salesorder_id}'
    headers = make_header(token)
    params = {
        'organization_id': org_id,
        'print': kwargs.get("print"),
        "accept": kwargs.get("accept")
    }
    response = requests.get(url=url, headers=headers, params=params)

    if response.status_code == 401:
        token.generate()
        return get_salesorder(token, org_id, salesorder_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("salesorder")


def delete_salesorder(token, org_id, salesorder_id):
    url = f'https://books.zoho.com/api/v3/salesorders/{salesorder_id}'
    headers = make_header(token)
    params = {
        'organization_id': org_id,
    }
    response = requests.delete(url=url, headers=headers, params=params)

    if response.status_code == 401:
        token.generate()
        return delete_salesorder(token, org_id, salesorder_id)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get('message')

    

def mark_status(token, org_id, salesorder_id, status="open"):
    url = f'https://books.zoho.com/api/v3/salesorders/{salesorder_id}/status/{status}'
    headers = make_header(token)
    params = {'organization_id': org_id}

    response = requests.post(url=url, headers=headers, params=params)
    if response.status_code == 401:
        token.generate()
        return mark_status(token, org_id, salesorder_id, status=status)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("message")


def email_salesorder(token, org_id, salesorder_id, to_mail_ids, subject, body, **kwargs):
    url = f'https://books.zoho.com/api/v3/salesorders/{salesorder_id}/email'
    headers = make_header(token)
    params = {'organization_id': org_id}

    data_object = kwargs
    data_object['to_mail_ids'] = to_mail_ids
    data_object['body'] = body
    data_object['subject'] = subject

    data = json.dumps(data_object).encode('utf-8')

    response = requests.post(url=url, headers=headers, params=params, data=data)

    if response.status_code == 401:
        token.generate()
        return email_salesorder(token, org_id, salesorder_id, to_mail_ids, subject, body, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("message")


def get_salesorder_email_content(token, org_id, salesorder_id, **kwargs):
    url = f'https://books.zoho.com/api/v3/salesorders/{salesorder_id}/email'
    headers = make_header(token)
    params = {
        'organization_id': org_id,
        'email_template_id': kwargs.get("email_template_id")
    }
    response = requests.get(url=url, headers=headers, params=params)

    if response.status_code == 401:
        token.generate()
        return get_salesorder_email_content(token, org_id, salesorder_id, **kwargs)

    else:
        content = json.loads(response.content.decode('utf-8'))
        return token, content.get("data")


def submit_for_approval(token, org_id, salesorder_id):
    url = f'https://books.zoho.com/api/v3/salesorders
