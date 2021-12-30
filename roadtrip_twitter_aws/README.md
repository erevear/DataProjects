<b>Analyze Twitter Data for Roadtripping Destinations</b><br>

![Visualize - OpenSearch - Google Chrome 2021-12-28 19-34-56_Moment (2)](https://user-images.githubusercontent.com/11822655/147722305-ec15db1c-afb8-45f3-ab58-46bb2eae4f61.jpg)

<b>Introduction</b><br>
This project is a pipeline to stream tweets from the Twitter API, move them into a Kinesis Firehose through to Opensearch, do some transformations with a Lambda function, and finally visualize the results in Opensearch Dashboard. 
The primary goal of the project was to learn about the various tools mentioned above, however, it was also a fun way to find out where people all over the world are heading on their roadtrips, and maybe get some ideas for new adventures.
<br>
<br>
<br>
<br>
<b>Pipeline</b><br>
![Roadtrip Twitter](https://user-images.githubusercontent.com/11822655/147527781-b246b0c1-2ad0-4b5d-bf0b-eec35110c76b.jpeg)
<b>1. Twitter API and Python</b><br>
Use the tweepy library to Stream data, and deliver it into a Kinesis Firehose Stream. The script filters for tweets where the tweeter mentions "roadtrip"<br>
<br>
<b>2. Kinesis Firehose Stream</b><br>
The Stream uses the Lambda described blow as part of its transformation. It also utilizes an index for future visualization in Opensearch<br>
<br>
<b>3. Lambda and Comprehend</b><br>
Send to a Lambda function for some processing. When looking through the Twitter API documentation, it would seem that the coordinates field would be the best option for obtaining a location for a mentioned roadtrip, however, after streaming hundreds of tweets it became clear that this was not often populated, and far more often the user mentioned the location directly in their Tweet. Of course this was quite messy, without standard spellings or representations, which presented an opportunity to use the Amazon Comprehend Service. We send the tweet to the Comprehend entity identification to have it pick out things it thinks are locations. We then sent these strings to the Google Maps API to pull in the latitude and longitude for mapping.<br>
<br>
<b>4. Amazon Opensearch Service</b><br>
Data with the latitude, longitude, and original tweet are all piped into Opensearch which integrates closely with the Opensearch Dashboards where we can map the latitude and longitude obtained from the location mentioned in the tweet. If we set the map to refresh every 5-10 seconds the visualization is semi live updating
<br>
<br>
<br>
<br>
<b>Next Steps</b><br>
<b>1.</b> Collect data over a longer period of time and do deeper analysis on popular destinations, most popular times of year, etc.</br>
<b>2.</b> Pull data through to JQuery or Node front end to create live updating webpage</br>
