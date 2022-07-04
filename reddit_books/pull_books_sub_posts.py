import requests
from datetime import datetime
import traceback
import time
import json
import sys
import csv

#this script pulls submissions from the r/books subreddit and dumps it to a csv. 
#It will run until it pulls everything or is stopped manually

#Based on: https://github.com/Watchful1/Sketchpad/blob/master/postDownloader.py

subreddit = "books"  # put the subreddit you want to download in the quotes
# leave either one blank to download an entire user's or subreddit's history
# or fill in both to download a specific users history from a specific subreddit

filter_string = f"subreddit={subreddit}"

url = "https://api.pushshift.io/reddit/{}/search?limit=1000&sort=desc&{}&before="

start_time = datetime.utcnow()


def downloadFromUrl(filename, object_type):
	print(f"Saving {object_type}s to {filename}")

	count = 0
	handle = open(filename, 'w', encoding="utf-8", newline="")
	csvWriter = csv.writer(handle,delimiter=str(','))
	previous_epoch = int(start_time.timestamp())
	while True:
		new_url = url.format(object_type, filter_string)+str(previous_epoch)
		json_text = requests.get(new_url, headers={'User-Agent': "Post downloader by /u/Watchful1"})
		time.sleep(1)  # pushshift has a rate limit, if we send requests too fast it will start returning error messages
		try:
			json_data = json_text.json()
		except json.decoder.JSONDecodeError:
			time.sleep(1)
			continue

		if 'data' not in json_data:
			break
		objects = json_data['data']
		if len(objects) == 0:
			break

		for object in objects:
			previous_epoch = object['created_utc'] - 1
			
			if object_type == 'submission':
				if object['is_self']:
					if 'selftext' not in object:
						continue

					if object['selftext'] == '[removed]':
						continue

					try:
						count += 1
						row_data = [object['title'], object['selftext'], object['score'], datetime.fromtimestamp(object['created_utc']).strftime("%Y-%m-%d")]
						csvWriter.writerow(row_data)
					except Exception as err:
						print(f"Couldn't print post: {object['url']}")
						print(traceback.format_exc())

		print("Saved {} {}s through {}".format(count, object_type, datetime.fromtimestamp(previous_epoch).strftime("%Y-%m-%d")))

	print(f"Saved {count} {object_type}s")
	handle.close()


downloadFromUrl("book_sub_posts.csv", "submission")