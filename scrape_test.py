import requests, oauth2, json
from pprint import pprint

with open('TWITTERCREDS.json', 'r') as credsfile:
	creds = json.loads(credsfile.read())

def oauth_req(url, key, secret, http_method='GET', post_body=b'', http_headers=None):
    consumer = oauth2.Consumer(key=creds.get('consumerKey'), secret=creds.get('consumerSecret'))
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

home_timeline = oauth_req( 'https://api.twitter.com/1.1/statuses/home_timeline.json', creds.get('accessToken'), creds.get('accessTokenSecret') )

pprint(json.loads(home_timeline), indent=2)