#!/bin/usr/python3.6

#https://twitter.com/search?q=(%23Hashtag)%20until%3A2019-08-19%20since%3A2019-08-12&src=typed_query
import requests,os,argparse,datetime,logging,json,csv

VALUE = "value"
CURSOR = "cursor"
TWEETS = "tweets"
FOLLOWERS = "followers"
USERNAME = "username"
USERID = "userid"
TWEETLINK = "tweetlink"
OPERATION = "operation"
CONTENT = "content"
TIMELINE = "timeline"
ENTRIES = "entries"
ENTRY = "entry"
REPLACEENTRY = "replaceEntry"
ADDENTRIES = "addEntries"
INSTRUCTIONS = "instructions"
GUEST_TOKEN = "guest_token"
GLOBALOBJECTS = "globalObjects"

class Manager:
    def __init__(self,args):
        self.fetch = Fetch()
        self.startDate = args.startDate
        self.endDate = args.endDate
        self.hashTag = args.hashTag
        self.startDay,self.endDay = self.assginDate(self.startDate,self.endDate)
        self.hashlink = "https://twitter.com/search?q=(%23{0})%20until%3A{1}%20since%3A{2}&src=typed_query"

    def assginDate(self,st=str,et=str):
        try:
            if st is None:
                st = format(datetime.date.today(), '%Y-%m-%d')
            if et is None:
                et = format(datetime.date.today() - datetime.timedelta(days=5), '%Y-%m-%d')
            return st,et
        except Exception as e:
            logging.error(e)
            return None,None
    
    def __run__(self):
        try:
            link = self.hashlink.format(self.hashTag,self.endDay,self.startDay)
            print(link)
            self.fetch.watch(link)
        except Exception as e:
            logging.error(e)
            return None

class Fetch:
    def __init__(self):
        self.cursorInt = 0
        self.TWEETDICT = dict()
        self.startHeader = int()
        self.cursor = "scroll:"
        self.GetTweetsUrl = "https://twitter.com/i/api/2/search/adaptive.json"
        self.GustTokenUrl = "https://api.twitter.com/1.1/guest/activate.json"

    def watch(self,Url=str):
        try:
            token = self.getGustToken()
            while True:
                tweets = self.getTweets(cursor=self.cursor,token=token,url=Url)
                if tweets is not None:
                    self.parserTweets(tweets)
        except Exception as e:
            logging.error(e)
            return None

    def parserTweets(self,_json=dict):
        try:
            mainParser = json.loads(_json)
            # print(mainParser)
            # input("#"*90)
            store_tweets = mainParser[GLOBALOBJECTS][TWEETS]
            self.getCursorLink(mainParser)
            for tweetId in store_tweets:
                userId = store_tweets[tweetId]["user_id_str"]
                timestamp = store_tweets[tweetId]["created_at"]
                retweet = store_tweets[tweetId]["retweet_count"]
                favorite = store_tweets[tweetId]["favorite_count"]
                reply = store_tweets[tweetId]["reply_count"]
                userName = mainParser[GLOBALOBJECTS]["users"][userId]["screen_name"]
                followers = mainParser[GLOBALOBJECTS]["users"][userId]["followers_count"]
                tweetlink = "https://twitter.com/{0}/status/{1}".format(userId,tweetId)
                row_data = [userId,userName,followers,timestamp,tweetlink,retweet,favorite,reply]
                self.csv_file_write(row_data)
            print(self.TWEETDICT)
        except Exception as e:
            logging.error(e)
            return None

    def getCursorLink(self,parser):
        try:
            parserContentCursor = parser[TIMELINE][INSTRUCTIONS][-1]
            if self.cursorInt < 1:
                self.cursor = parserContentCursor[ADDENTRIES][ENTRIES][-1][CONTENT][OPERATION][CURSOR][VALUE]
                self.cursorInt += 1
            else:
                self.cursor = parserContentCursor[REPLACEENTRY][ENTRY][CONTENT][OPERATION][CURSOR][VALUE]
        except Exception as e:
            logging.error(e)
            return None

    def getTweets(self,cursor=str,token=str,url=str):
        try:
            headers = {
                'authority': 'twitter.com',
                'x-twitter-client-language': 'en-GB',
                'sec-ch-ua-mobile': '?0',
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'user-agent': 'Mozilla/5.0',
                'x-guest-token': token,
                'x-twitter-active-user': 'yes',
                'accept': '*/*',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': url,
                'accept-language': 'en-GB,en;q=0.9',
            }
            params = (
                ('include_profile_interstitial_type', '1'),
                ('include_blocking', '1'),
                ('include_blocked_by', '1'),
                ('include_followed_by', '1'),
                ('include_want_retweets', '1'),
                ('include_mute_edge', '1'),
                ('include_can_dm', '1'),
                ('include_can_media_tag', '1'),
                ('skip_status', '1'),
                ('cards_platform', 'Web-12'),
                ('include_cards', '1'),
                ('include_ext_alt_text', 'true'),
                ('include_quote_count', 'true'),
                ('include_reply_count', '1'),
                ('tweet_mode', 'extended'),
                ('include_entities', 'true'),
                ('include_user_entities', 'true'),
                # ('include_ext_media_color', 'true'),
                ('include_ext_media_availability', 'true'),
                ('send_error_codes', 'true'),
                ('simple_quoted_tweet', 'true'),
                ('q', '(#VijayTheMaster) until:2020-12-26 since:2020-12-25'),
                ('count','200000'),
                ('query_source', 'typed_query'),
                ('cursor', cursor),
                ('pc', '1'),
                ('spelling_corrections', '1'),
                # ('ext', 'mediaStats,highlightedLabel'),
            )
            # print(params)
            response = self.requests_body(self.GetTweetsUrl,"GET",headers=headers,params=params)
            if response is not None:
                return response
            return None
        except Exception as e:
            logging.error(e)
            return None

    def getGustToken(self):
        try:
            headers = {
                "User-Agent": "Firefox",
                'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            }
            responce = self.requests_body(self.GustTokenUrl,"POST",headers=headers)
            jsoncontent = json.loads(responce)[GUEST_TOKEN]
            return jsoncontent
        except Exception as e:
            logging.error(e)
            return None

    def requests_body(self,url=str,method=str,headers=None,params=None):
        try:
            if headers is None:
                headers = {"User-Agent": "Firefox"}
            if params is None:
                params = ()
            response = requests.request(method,url,headers=headers,timeout=60,params=params)
            if response.status_code == 200:
                contentResponse = response.text
                return contentResponse
            return None
        except Exception as e:
            logging.error(e)
            return None
            
    def csv_file_write(self,data):
        try:
            with open('turkcell_tweets.csv', mode='a') as f:
                fs = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                if self.startHeader <= 0:
                    header = ['UserId', 'Handle', 'Followers', 'Timestamp', 'TweetLink', 'Retweets', 'Likes','Comments']
                    fs.writerow(header)
                    self.startHeader += 1
                fs.writerow(data)
                print(data)
            f.close()
            return True
        except Exception as e:
            logging.error(e)
            return None

if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    parser = argparse.ArgumentParser()
    parser.add_argument("-st","--startDate",help="from yyyy-mm-dd",default=None)
    parser.add_argument("-et","--endDate",help="to yyyy-mm-dd",default=None)
    parser.add_argument("-s","--hashTag",help="search hash",required=True)
    args = parser.parse_args()
    Manager(args).__run__()