from elasticsearch import Elasticsearch, helpers
import json
import gzip
from elasticsearch_dsl import Index
import csv
import sys


#TO RUN start ES: elasticsearch-8.2.3\bin\elasticsearch.bat

ELASTIC_PASSWORD = "{ELASTIC_PASSWORD}"


def connect_elasticsearch():
	_es = None
	_es = Elasticsearch(
		"https://localhost:9200",
		ca_certs="{ES_URL}",
		basic_auth=("{username}", ELASTIC_PASSWORD),
		http_auth=("{username}", ELASTIC_PASSWORD)
	)
	if _es.ping():
		print('Connection successful')
	else:
		print('Elasticsearch unavailable')
	return _es



if __name__ == '__main__':
    es = connect_elasticsearch()
    del_ind = es.indices.delete(index='bulk_openlib', ignore=[400, 404])

    maxInt = sys.maxsize

    #set the maxsize of load to avoid overflow error
    while True:
    	try:
    		csv.field_size_limit(maxInt)
    		break
    	except OverflowError:
    		maxInt = int(maxInt/10)

 
    with open('ol_dump_works_2022-06-06_w_parsed.csv','r', encoding='utf-8') as inputfile:
    	data = csv.DictReader(inputfile, quoting=csv.QUOTE_NONE)
    	loaded = helpers.bulk(es, data, index='bulk_openlib',chunk_size=500, request_timeout=2000)


