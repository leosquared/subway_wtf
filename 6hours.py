import requests, oauth2, json, csv, datetime, pandas as pd, re, numpy as np
from urllib.parse import urlencode
from pprint import pprint

def api_response():
    """ obtains tweets for the last 6 hours
    then compile some statistics in response """

    ## Credentials & Connection to API Client
    with open('TWITTERCREDS.json', 'r') as credsfile:
    	creds = json.loads(credsfile.read())

    def api_client(consumer_key, consumer_secret, access_token, access_token_secret):
        """ established api client """

        consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
        token = oauth2.Token(key=access_token, secret=access_token_secret)
        client = oauth2.Client(consumer, token)
        return client

    ## Processing Tweets
    def tag(tweet):
        """ Identify train in each tweet and classification """

        p_train = re.compile(r'(?<=#)\w+(?=train)')
        p_delay = re.compile(r'Delay|delay|suspended')
        p_service = re.compile(r'Service|service')
        p_planned = re.compile(r'Planned|planned')
        trains = re.findall(p_train, tweet) or 0
        delay = 1 if re.search(p_delay, tweet) else 0
        service = 1 if re.search(p_service, tweet) else 0
        planned = 1 if re.search(p_planned, tweet) else 0
        return {'trains':trains, 'delay':delay, 'service':service, 'planned':planned}

    def final_response(tweets_data):
        """ organizes data into response """

        df = pd.io.json.json_normalize(tweets_data
                , [['tags', 'trains']]
                , ['tweet_id', 'tweet', 'timestamp'
                   , ['tags', 'delay'], ['tags', 'service'], ['tags', 'planned']]
            )
        df = df.rename(columns={0:'train'})
        res = json.loads(df.groupby('train').agg(np.sum)[['tags.delay', 'tags.service', 'tags.planned']].to_json())
        return res

    ## twitter search API variables
    search_endpoint = 'https://api.twitter.com/1.1/search/tweets.json'
    search_term = urlencode({
        'q':'from:SubwayStats -filter:retweets -filter:replies'
        , 'count':100
    })
    url = f'{search_endpoint}?{search_term}'
    client = api_client(
            creds.get('consumerKey')
            , creds.get('consumerSecret')
            , creds.get('accessToken')
            , creds.get('accessTokenSecret')
        )
    next_q = None
    tweets_data = []

    ## Ping API
    while next_q != '':
        r = client.request(url, method='GET', body=b'', headers=None)
        statuses = json.loads(r[1]).get('statuses')
        next_q = json.loads(r[1]).get('search_metadata').get('next_results', '')
        url = search_endpoint+next_q

        for status in statuses:
            if datetime.datetime.utcnow()-datetime.timedelta(hours=6) <= pd.to_datetime(status.get('created_at'), infer_datetime_format=True):
                tweets_data.append({
                    'tweet_id':status.get('id')
                    , 'tweet':status.get('text')
                    , 'timestamp':status.get('created_at')
                    , 'tags':tag(status.get('text'))
                })
        print('received {} tweets'.format(len(statuses)))

    ## final response
    return final_response(tweets_data)