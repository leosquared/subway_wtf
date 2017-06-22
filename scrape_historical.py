import requests, oauth2, json, csv, time
from urllib.parse import urlencode
from pprint import pprint

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
    , 'count':50
    # , 'until':'2017-01-31'
})
url = f'{search_endpoint}?{search_term}'
client = api_client(
        creds.get('consumerKey')
        , creds.get('consumerSecret')
        , creds.get('accessToken')
        , creds.get('accessTokenSecret')
    )
next_q = None

with open('status_historical.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(('tweet_id', 'tweet_content', 'timestamp'))
    while next_q != '':
        r = client.request(url, method='GET', body=b'', headers=None)
        statuses = json.loads(r[1]).get('statuses')
        next_q = json.loads(r[1]).get('search_metadata').get('next_results', '')
        print(json.loads(r[1]).get('search_metadata'))
        url = search_endpoint+next_q
        fmt_statuses = [("'"+x.get('id_str'), x.get('text'), x.get('created_at')) for x in statuses]
        print('received {} statuses'.format(len(statuses)))
        writer.writerows(fmt_statuses)
