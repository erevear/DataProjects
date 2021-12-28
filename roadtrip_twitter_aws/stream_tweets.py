import boto3
import random
import time
import json
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream

import config

access_token = config.twitter_stream_credentials['access_token']
access_token_secret = config.twitter_stream_credentials['access_token_secret']
consumer_key = config.twitter_stream_credentials['consumer_key']
consumer_secret = config.twitter_stream_credentials['consumer_secret']

aws_key_id =  config.aws_keys['aws_key_id']
aws_key =  config.aws_keys['aws_key']

DeliveryStreamName = 'twitter_stream'

client = boto3.client('firehose', region_name='us-west-2',
                          aws_access_key_id=aws_key_id,
                          aws_secret_access_key=aws_key
                          )

class StdOutListener(tweepy.Stream):

    def on_data(self, data):
        client.put_record(DeliveryStreamName=DeliveryStreamName,Record={'Data': data})

        print(json.loads(data))
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':

    twitter_stream = StdOutListener(consumer_key, consumer_secret, access_token, access_token_secret)

    twitter_stream.filter(track=['roadtrip'])