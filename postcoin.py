import json, requests, csv
from bs4 import BeautifulSoup
import pandas as pd
from .auth import credentials
import tweepy

#setting headers for requests
headers = {
    'User-agent': 'Mozilla/5.0'}

#setting the url for scraping coin data
base_url = "https://www.coingecko.com"

#creating a dictionary to append all the scraped data
tables = []

#running a for loop to get crypto coins data from the first 2 pages
for i in range(1,3):
    params = {
        'page': i
    }
    print(i)
    response = requests.get(base_url, headers=headers, params=params)
    soup = BeautifulSoup(response.content,'html.parser')
    #saving the data to the dictionary
    tables.append(pd.read_html(str(soup))[0])

#using panda to concatenate the tables and remove first and last 3 lines from the scraped data, 
#and then saving it to a CSV file
master_table = pd.concat(tables)
master_table = master_table.loc[:,master_table.columns[1:-3] ]
master_table.to_csv('crypto.csv', index=False)

#defining a function to turn CSV to JSON
def make_json(csvFilePath, jsonFilePath):
    data = {}
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
             
            key = rows['Coin']
            data[key] = rows
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

csvFilePath = r'crypto.csv'
jsonFilePath = r'writefromweb.json'

#using function to turn CSV to JSON
make_json(csvFilePath, jsonFilePath)

#using separator to remove lines from key name
separator = " "

#open the saved json file to modify the key name
with open('writefromweb.json', 'r+') as json_file:
    data = json.load(json_file)

for key in list(data):
    title = key
    title = title.split(separator, 2)[-1]
    title = title.split(separator, 1)[-1]
    data[title] = data.pop(key)

#open a new file to avoid an error on writing, and dump data there
with open('read.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

#authenticating to twitter
client = tweepy.Client(credentials['bearer_token'],credentials['api_key'], credentials['api_secret'], credentials['access_token'], credentials['access_token_secret'])
auth = tweepy.OAuth1UserHandler(credentials['api_key'], credentials['api_secret'], credentials['access_token'], credentials['access_token_secret'])
api = tweepy.API(auth)

#opening news!
b = True
while b:
    with open("read.json", "r") as f:
        a = json.load(f)
    b = False

#making a dictionary to append all the tweets
tweetlist = []

#picking what coins to post on twitter
coins = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE']

#defining a function to make the tweet, for future upgrades to the script.
def maketweet():
    for coin in coins:
        if "-" in a[f"{coin}"]['24h']:
            sign = "down"
        else:
            sign = "up"
        tweetcoin = f"#{coin} : {a[f'{coin}']['Price'][0:10]}, 24H it's {sign} {a[f'{coin}']['24h']}\n"
        tweetlist.append(tweetcoin)

    tweet = "Latest Crypto Prices, hourly update.\n" \
        f"{tweetlist[0]}" \
        f"{tweetlist[1]}"\
        f"{tweetlist[2]}"\
        f"{tweetlist[3]}"\
        f"{tweetlist[4]}"\
        f"{tweetlist[5]}"
    return tweet

tweet = maketweet()

#check if the length of the tweet is more than 280..
if len(tweet) > 10 and len(tweet) < 280:
    print(tweet)
    try:
        #post tweet!
        client.create_tweet(text = f"{tweet}")

    except Exception as e:
        #catching an error(duplicate posting error.) and printing it, to see if another error might have occured.
        print(e)
        pass

