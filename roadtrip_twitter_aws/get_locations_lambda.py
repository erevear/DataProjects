from __future__ import print_function

import base64
import json
import boto3
import requests
from collections import defaultdict

print('Loading function')

def get_comprehend_entities(text):
	comprehend = boto3.client(service_name='comprehend', region_name='us-east-2', )
	comprehend_results = json.dumps(comprehend.detect_entities(Text=text, LanguageCode='en'), sort_keys=True, indent=4)
	comprehend_results = json.loads(comprehend_results)
	return comprehend_results


def build_geonames_url(word):
	url = "http://api.geonames.org/wikipediaSearchJSON?q=" + word + "&maxRows=1000&username={username}"


def pull_google_maps_location(place_name):
	url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + place_name + "&key={key}"
	response = requests.get(url)
	return response.content


def pull_geonames(place_name):
	url = "http://api.geonames.org/wikipediaSearchJSON?q=" + place_name + "&maxRows=10&username={username}"
	response = requests.get(url)
	return response.content


def parse_google_maps_results(google_maps_results):
	place_data = {}
	place_data["title"] = google_maps_results["results"][0]["address_components"][0]["long_name"]
	place_data["latitude"] = google_maps_results["results"][0]["geometry"]["location"]["lat"]
	place_data["longitude"] = google_maps_results["results"][0]["geometry"]["location"]["lng"]
	print(place_data)
	return place_data


def parse_geonames(geonames_results):
	places = []
	for place in geonames_results["geonames"]:
		place_data = {}
		place_data["title"] = place["title"]
		place_data["latitude"] = place["lat"]
		place_data["longitude"] = place["lng"]
		place_data["wikipediaUrl"] = place["wikipediaUrl"]
		places.append(place_data)
	return places

def get_data_dict_json(comprehend_entities):
    for entity in comprehend_entities:
            entity_text = entity["Text"].replace("#","")
            entity_type = entity["Type"]
            if entity_type == "LOCATION":
                google_maps_results = pull_google_maps_location(entity_text)
                google_maps_place = parse_google_maps_results(json.loads(google_maps_results))
                if google_maps_place:
                    matched_place_dict = {}
                    matched_place_dict["title"] = google_maps_place["title"]
                    matched_place_dict["latitude"] = google_maps_place["latitude"]
                    matched_place_dict["longitude"] = google_maps_place["longitude"]
                    print(matched_place_dict)
                    return matched_place_dict

def lambda_handler(event, context):
    output = []

    for record in event['records']:
        
        tweet_text = json.loads(base64.b64decode(record['data']).decode('utf-8').strip())['text']
        print(tweet_text)
        

        comprehend_entities = get_comprehend_entities(tweet_text)["Entities"]
        print(comprehend_entities)
        matched_place_json = get_data_dict_json(comprehend_entities)
        if matched_place_json:
            data_record = {
                
                'tweet':tweet_text,

                'geopnt':[matched_place_json['longitude'], matched_place_json['latitude']]
            }
            print(data_record)
            
            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(json.dumps(data_record).encode('utf-8')).decode('utf-8')
            }
            print(output_record)
            
            output.append(output_record)

    print(output)
    return {'records': output}