import requests 
import json
from datetime import datetime
import time
import csv
import os
from pathlib import Path


WRITE_OPERATIONS = ['insert', 'update', 'upsert']


def make_header(token):
	return {
		"Authorization": f"Zoho-oauthtoken {token.access}",
		"Content-Type": "application/json"
	}

############ BULK READ JOBS 

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
		input(f"Your data has arrived: '{filename}' >>>>> ")
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

	os.system("clear")
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
		#token, response = fetch_bulk_read(token, job_obj)
		#input("Enter to exit the script >>> ")
		return fetch_bulk_read(token, job_obj)
		

	else:
		os.system("clear")
		print(f"Download URL >>>> {download_url}")
		input("Enter to continue >>>> ")
		#raise SystemExit()
		return token, job_obj

	raise SystemExit()

######### BULK WRITE

def make_upload_header(token, org_id):
	return {
		'Authorization': f'Zoho-oauthtoken {token.access}',
		'feature': 'bulk-write',
		'X-CRM-ORG': org_id
	}
		#'Content-Type': "multipart/form-data"
	#}

def upload_csv(token, org_id, module, filename):
	url = "https://content.zohoapis.com/crm/v3/upload"
	headers = make_upload_header(token, org_id)
	with open(filename, 'rb') as upload_file:
		request_body = {'file': upload_file}
		#files = ('file', upload_file)
		#request_body = [files]
		#payload = {}

		response = requests.post(url=url, headers=headers, data=request_body)
		print(response.headers)
	#files = {"file": open(filename, 'rb')}

	#response = requests.post(url=url, headers=headers, files=files)
	print(response.status_code)
	print(response.content)
	input("....")
	if response.status_code == 200:
		print("There was an error with the file format or size")
		input("continue >>> ")
		return upload_csv(token,org_id,module, filename)

	elif response.status_code >= 400 and response.status_code < 500:
		print(response.status_code)
		print(response.reason)
		print(response.text)
		print(response.headers)
		print("Refreshing token")
		token.generate()
		return upload_csv(token,org_id, module, filename)

	else:
		content = json.loads(response.content.decode('utf-8'))
		print(f"Status: {content['status']}")
		print(f"{content['message']}")
		job_details = content['details']
		print(f"Job ID: {job_details['file_id']}")
		return create_bulk_write(token, module, job_details)


def create_bulk_write(token, module, file_details, **kwargs):
	url = 'https://www.zohoapis.com/crm/bulk/v3/write'
	headers = make_header(token)

	request_body = {}
	if kwargs.get("operation") is None or kwargs.get("operation") not in WRITE_OPERATIONS:
		operation = "insert"

	request_body['operation'] = operation 
	request_body['ignore_empty'] = kwargs.get("ignore_empty")


	resource_obj = {}
	resource_obj['type'] = 'data'
	resource_obj['module'] = module
	resource_obj['file_id'] = file_details['file_id']
	resource_obj['find_by'] = kwargs.get("find_by")
	resource_obj["field_mappings"] = kwargs.get("field_mappings")

	request_body['resource'] = [resource_obj]

	if kwargs.get("callback") is not None:
		pass

	data = json.dumps(request_body).encode('utf-8')

	response = requests.post(url=url, headers=headers, data=data)
	if response.status_code >= 400 and response.status_code < 500:
		print("Refreshing token")
		token.generate()
		return create_bulk_write(token, module, file_details, **kwargs)
	else:
		content = json.loads(response.content.decode('utf-8'))
		status = content['status']
		message = content['message']
		job_details = content.get("details")
		if job_details is None:
			raise Exception
		return bulk_write_updates(token, job_details)


def bulk_write_updates(token, job_details):
	progress = {
		"added_count": 0,
		"skipped_count": 0,
		"updated_count": 0,
		"total_count": 0
	}
	status = job_details.get("status")
	job_id = job_details.get("id")
	url = f'https://www.zohoapis.com/crm/bulk/v3/write/{job_id}'
	headers = make_header(token)

	while status != "COMPLETED":
		os.system('clear')
		print(f'Your bulk write job currently has a status of {status}.')
		time.sleep(0.5)
		print("Fetching another status update in 10 seconds...")
		time.sleep(0.5)
		print("Press CTRL + C to skip the wait and fetch the status of the job >>>> ")
		time_left = 10
		while time_left > 0:
			try:

				os.system('clear')
				time.sleep(1)
				time_left -= 1

			except KeyboardInterrupt:
				os.system('clear')
				print("Fetching a status update")
				time.sleep(2.7)
				time_left = 0
		os.system('clear')
		print("Fetching a status update")
		response = requests.get(url=url, headers=headers)
		if response.status_code >= 400 and response.status_code < 500:
			print("Refreshing token")
			token.generate()
				#return bulk_write_updates(token, job_details)
			continue

		else:

			content = json.loads(response.content.decode('utf-8'))
			resource_obj = content['resource'][0]
			results_obj = content['results']
			status = content['status']
			#status = content.get("status")
			if status == "ADDED":
				print("Your bulk write job has successfully been added.")
				input("Continue >>> ")
				continue
			elif status == "INPROGRESS":
				
				file_stats = resource_obj['file']
				print(f'Your bulk write job for the file {file_stats["name"]} is in progress.')
				time.sleep(0.5)
				progress['added_count'] = file_stats['added_count']
				progress['skipped_count'] = file_stats['skipped_count']
				progress['updated_count'] = file_stats['updated_count']
				progress['total_count'] = file_stats['total_count']
				print(progress)
				input("Continue >>> ")
				continue
	print("Your bulk write job has been completed")
	time.sleep(0.5)
	file_stats = resource_obj['file']
	download_url = result['download_url']
	progress['added_count'] = file_stats['added_count']
	progress['skipped_count'] = file_stats['skipped_count']
	progress['updated_count'] = file_stats['updated_count']
	progress['total_count'] = file_stats['total_count']
	print(progress)
	prompt = str(input("[y/Y] to download the final result, [n/N] to just receive the URL >>> "))
	prompt = prompt.strip().upper()
	if "Y" in prompt:
		os.system('clear')
		print("Fetching the result of the bulk write job as a CSV file.")
		#token, response = fetch_bulk_write(token )
		print("In dev")
		#raise SystemExit()
		return token, file_stats

	else:
		os.system('clear')
		print(f'Download URL >>> {download_url}')
		input("Enter to exit this script >>> ")
		#raise SystemExit()
		return token, file_stats
	#raise SystemExit()



			