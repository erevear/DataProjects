import csv
import sys
import json
import gzip

#This script pulls just the titles from the openlib data dump in order to keep data small
#for elasticsearch bulk upload

#set max size of fields in csv to avoid overflow error
maxInt = sys.maxsize

while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

with open("ol_dump_authors_2022-06-06.txt") as fr, open("ol_dump_authors_2022-06-06_w_parsed.csv","w",newline='', encoding='utf-8') as fw:
    cr = csv.reader(fr,delimiter='\t', quoting=csv.QUOTE_NONE)
    cw = csv.writer(fw)
    cw.writerow(['title'])
    rows = []
    for row in cr:
        # print(row)
        book_row = []
        row_json = json.loads(row[4])
        print(row_json)
        if 'title' in row_json:
            book_row.append(row_json['title'])
        else:
            book_row.append('')

        
        cw.writerow(book_row)