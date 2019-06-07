import os
import requests
from pymongo import MongoClient
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client-secret.json"

client = MongoClient("mongodb+srv://{}:{}@cluster0-xgdbi.mongodb.net/test?retryWrites=true&w=majority".format(str(os.getenv("user")),str(os.getenv("password"))))

db = client.get_database('KartikBot')
advice_collection = db.advice
jobs_collection = db.jobs

import dialogflow_v2 as dialogflow
dialogflow_session_client = dialogflow.SessionsClient()
PROJECT_ID = "kartikbot-tgsfvw"

def get_jobs(parameters):
    url = ""
    if parameters.get('geo-country') == '':
        url = "https://jobs.github.com/positions.json?search={}&location={}".format(parameters.get('lang_name'),parameters.get('geo-city'))
    else:
        url = "https://jobs.github.com/positions.json?search={}&location={}".format(parameters.get('lang_name'),parameters.get('geo-country'))
    print(url)
    jobs_list = requests.get(url)
    # print(jobs_list.json())
    return jobs_list.json()


def detect_intent_from_text(text, session_id, language_code='en'):
    session = dialogflow_session_client.session_path(PROJECT_ID, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = dialogflow_session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result


def fetch_reply(msg, session_id):
    response = detect_intent_from_text(msg, session_id)
    counter = 0
    if response.intent.display_name == 'search_jobs':

        jobs_collection.update_one({'number':session_id},{'$push': {'queries':msg}},upsert=True)
        jobs = get_jobs(dict(response.parameters))
        jobs_str = 'Here are some jobs :'
        for row in jobs:
            if(counter >= 5):
                break
            jobs_str += "\nType: {}\nURL: {}\nCompany: {}\nCompany URL: {}\nLocation: {}\nTitle: {}\n\n".format(row['type'],row['url'],row['company'],row['company_url'],row['location'],row['title'])
            counter += 1
        return jobs_str
    elif response.intent.display_name == 'give_advice':
        advice_url = "https://api.adviceslip.com/advice"
        advice = requests.get(advice_url)
        try:
            advice_collection.update_one({'number':session_id},{'$push':{'advices':advice.json()['slip']['advice']}},upsert=True)
        except Exception as e:
            print(e)
        return "_*{}*_".format(advice.json()['slip']['advice'])
    else:
        return response.fulfillment_text