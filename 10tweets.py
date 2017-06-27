import unzip_requirements
import requests, oauth2, json, csv, time
from urllib.parse import urlencode
from pprint import pprint

def get_tweets(event, context):
    with open('TWITTERCREDS.json', 'r') as credsfile:
        creds = json.loads(credsfile.read())

    def api_client(consumer_key, consumer_secret, access_token, access_token_secret):
        consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
        token = oauth2.Token(key=access_token, secret=access_token_secret)
        client = oauth2.Client(consumer, token)
        return client

    search_endpoint = 'https://api.twitter.com/1.1/search/tweets.json'
    search_term = urlencode({
        'q':'from:NYCTSubway -filter:retweets -filter:replies'
        , 'count':10
    })
    url = f'{search_endpoint}?{search_term}'
    client = api_client(
            creds.get('consumerKey')
            , creds.get('consumerSecret')
            , creds.get('accessToken')
            , creds.get('accessTokenSecret')
        )
    r = client.request(url, method='GET', body=b'', headers=None)
    statuses = json.loads(r[1]).get('statuses')
    fmt_statuses = [{'tweet_id':x.get('id'), 'text':x.get('text'), 'created_time':x.get('created_at')} for x in statuses]

    response = {
        'statusCode': 200
        , 'body': json.dumps(fmt_statuses)
    }

    return response
