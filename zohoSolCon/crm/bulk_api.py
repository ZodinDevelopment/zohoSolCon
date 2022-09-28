import requests 
import json
from datetime import datetime
import time
import csv
import os
from pathlib import Path


def make_header(token):
	return {
		"Authorization": f"Zoho-oauthtoken {token.access}",
		"Content-Type": "application/json"
	}


def create_bulk_read(token, module, **kwargs):
	url = "https://www.zohoapis.com/crm/bulk/v3/read"
	headers = make_header(token)
	data_object = {}
	callback = kwargs.get("callback")
	if callback is not None:
		data_object['callback'] = callback
	query_object = {}
	query_object['module'] = {'api_name': module}
	file_type = kwargs.get("file_type")
	if file_type is not None:
		file_type = "csv"
	query_object['file_type'] = file_type

	data_object['query'] = query_object
	#request_body = {"data": data_object}


	data = json.dumps(data_object).encode('utf-8')
	response = requests.post(url=url, headers=headers, data=data)
	print(response.status_code)
	print(response.content)
	if response.status_code == 401:
		token.generate()
		return create_bulk_read(token, module, **kwargs)

	else:
		content = json.loads(response.content.decode('utf-8'))
		data = content.get("data")[0]
		status = data.get("status")
		msg = data.get("message")
		details = data.get("details")
		return bulk_read_updates(token, details)




def fetch_bulk_read(token, job_obj):
	job_id = job_obj['id']
	url = f'https://www.zohoapis.com/crm/bulk/v3/read/{job_id}/result'
	headers = make_header(token)
	response = requests.get(url=url, headers=headers)
	if response.status_code == 401:
		token.generate()
		return fetch_bulk_read(token, job_obj)
	else:
		filename = Path(f"bulk_read{job_id}.zip")
		filename.write_bytes(response.content)
		input(f"Your data has been arrived: '{filename}' >>>>> ")
		return token, filename


def bulk_read_updates(token, job_details):

	status = job_details.get("status")
	job_id = job_details.get("id")
	url = f"https://www.zohoapis.com/crm/bulk/v3/read/{job_id}"
	headers = make_header(token)
	while status != "COMPLETED":
		os.system("clear")
		print(f"Your bulk read job currently has a status of {status}.")
		time.sleep(0.5)
		print("Fetching a status update in 300 seconds...")
		time.sleep(0.5)
		print("Press CTRL + C to skip the wait and fetch a status update >>> ")
		time_left = 300
		while time_left > 0:
			try:
				
				print(time_left)
				time.sleep(1)
				time_left -= 1

			except KeyboardInterrupt:
				
				os.system('clear')
				print("Fetching a status update")
				time.sleep(2.7)
				time_left = 0
		response = requests.get(url=url, headers=headers)
		if response.status_code == 401:
			token.generate()
			continue
		else:
			content =  json.loads(response.content.decode('utf-8'))
			data = content.get("data")[0]
			status = data.get("state")

	os.system("cear")
	print("Your bulk read job is marked as COMPLETED")	
	time.sleep(0.5)
	results = data.get("result")
	page = results['page']
	count = results['count']
	more = results['more_records']
	download_url = results['download_url']
	print(f"IMPORTANT download URL: {download_url}")
	job_obj = {
		"page": page, 
		"count": count,
		"more": more,
		"download_url": download_url,
		"status": status,
		"id": job_id


	}

	prompt = str(input("[y/Y] to begin downloading resource, [n/N] to just receive your bulk read URL >>> "))
	prompt = prompt.strip().upper()
	if "Y" in prompt:
		os.system('clear')
		print("Fetching your CSV Bulk Read job")
		token, response = fetch_bulk_read(token, job_obj)
		input("Enter to exit the script >>> ")

		

	else:
		os.system("clear")
		print(f"Download URL >>>> {download_url}")
		input("Enter to continue >>>> ")
		raise SystemExit()

	raise SystemExit()





			