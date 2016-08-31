

import flask
import httplib2, argparse, os, sys, json
from oauth2client import tools, file, client
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from googleapiclient.errors import HttpError

project_id = 'raxlearn'
model_id = 'raxmodel'


def main():
    train_model()
    pass

def train_model():
	""" Create new classification model """

	api = get_prediction_api()

	print("Creating new Model.")

	api.trainedmodels().insert(project=project_id, body={
		'id': model_id,
		'storageDataLocation': 'wine_data/wines.txt',
		'modelType': 'CLASSIFICATION'
	}).execute()

def get_prediction_api(service_account=True):
	scope = [
		'https://www.googleapis.com/auth/prediction',
		'https://www.googleapis.com/auth/devstorage.read_only'
	]
	api = get_api('prediction', scope, service_account)
	return api


def get_api(api, scope, service_account=True):
	""" Build API client based on oAuth2 authentication """
	STORAGE = file.Storage('oAuth2.json') #local storage of oAuth tokens
	credentials = STORAGE.get()
	if credentials is None or credentials.invalid: #check if new oAuth flow is needed
		if service_account: #server 2 server flow
			credentials = ServiceAccountCredentials.from_json_keyfile_name('service_key.json', scopes=scope)
			STORAGE.put(credentials)
		else: #normal oAuth2 flow
			CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
			FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS, scope=scope)
			PARSER = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[tools.argparser])
			FLAGS = PARSER.parse_args(sys.argv[1:])
			credentials = tools.run_flow(FLOW, STORAGE, FLAGS)

	#wrap http with credentials
	http = credentials.authorize(httplib2.Http())
	return discovery.build(api, "v1.6", http=http)


if __name__ == '__main__':
	main()