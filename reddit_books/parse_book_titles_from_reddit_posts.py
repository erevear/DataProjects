import requests
import pandas as pd
from datetime import datetime
import math
from fuzzywuzzy import fuzz
import csv
from collections import Counter
import re
import operator
from elasticsearch import Elasticsearch


#This script breaks reddit post titles into chunks and uses full text search with fuzzy matching
#to check them them against the elasticsearch database we built in a previous script

#uses script pieces from: https://github.com/AlessandroMozzato/hn_books/blob/master/hackernews_api_analysis.ipynb
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


def es_query(text):
    matches = set()
    es = connect_elasticsearch()

    result = es.search(
        index='bulk_openlib',
        query={'match': {'title': {'query':text , 'minimum_should_match':len(text.split(' ')), 'fuzziness':'AUTO'}}}
        )

    hits = result['hits']['hits']
    if len(hits) > 0:
        top_match = hits[0]['_source']['title']
        #check if lengths match to at least filter out things at a high level that couldn't be the book title
        if len(top_match.split(' ')) == len(text.split(' ')):
            matches.add(top_match)

    return matches


def createNGrams(post_title):
    all_matches = set()
    text_clean = [re.sub(r"[^a-zA-Z0-9]+", ' ', k)  for k in post_title.split("\n")]


    countsb = Counter()
    countst = Counter()
    countsq = Counter()
    countsc = Counter()
    countsf = Counter()
    countss = Counter()

    words = re.compile(r'\w+')
    for t in text_clean:
        w = words.findall(t.lower())
        countsb.update(zip(w,w[1:]))
        countst.update(zip(w,w[1:],w[2:]))
        countsq.update(zip(w,w[1:],w[2:],w[3:]))
        countsc.update(zip(w,w[1:],w[2:],w[3:],w[4:]))
        countsf.update(zip(w,w[1:],w[2:],w[3:],w[4:],w[5:]))
        countss.update(zip(w,w[1:],w[2:],w[3:],w[4:],w[5:],w[6:]))


    results = {}

    results[1] = sorted(
        countsb.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    results[2] = sorted(
        countst.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    results[3] = sorted(
        countsq.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    results[4] = sorted(
        countsc.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    results[5] = sorted(
        countsf.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    results[6] = sorted(
        countss.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    # print(results)

    stops = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", 
         "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", 
         "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", 
         "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
         "have", "has", "had", "having", "do", "does", "did", "doing", "and", "an", "a", "the",  "but", 
         "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", 
         "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", 
         "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", 
         "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", 
         "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", 
         "s", "t", "can", "will", "just", "don", "should", "now", 'https', "www", "goodreads", "didn", "isn", "doesn",
        "recommend"]

    df = {}

    for k in [1,2,3,4,5,6]:
        names = []
        counts = []
        for c in results[k]:
            lst = list(c[0])
            lst = [w for w in lst if ((w not in stops) and w.isalpha())]
            if len(lst)>0:
                names.append(' '.join(c[0]))
                counts.append(c[1])
        df[k] = pd.DataFrame(data={'names':names, 'counts':counts})
    for jj in [1,2,3,4,5,6]:
        df[jj]['title'] = None
        df[jj]['author'] = None

        for it in df[jj].iterrows():
            name = it[1]['names']
            #search chunk in elasticsearch bulk openlib
            match_set = es_query(name)
            all_matches.update(match_set)
    return all_matches


def main():
    posts = pd.read_csv('book_sub_posts.csv', names=["title", "description", "score", "date"]) 
    
    final_res = []
    with open("new_file_w_openlib.csv","w+", encoding="utf-8", newline="") as my_csv:
        csvWriter = csv.writer(my_csv,delimiter=str(','))
        for index, post in posts.iterrows():
            if index%500 == 0:
                print('processed ' + str(index) + ' files')
        
            if post['title']:
                results = createNGrams(post['title'])
                if results:
                    
                    for result in results:
                        post_copy = post.values.tolist()
                        post_copy.append(result)
                        #remove spaces and newlines
                        post_copy = [str(field).replace(',','').replace('\n','') for field in post_copy]
    
                        csvWriter.writerow(post_copy)
                else:
                    post = post.values.tolist()
                    post.append('')
                    post = [str(field).replace(',','').replace('\n','') for field in post]
                    csvWriter.writerow(post)




if __name__ == '__main__':
    main()