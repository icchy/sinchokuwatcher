# coding:utf-8

import tweepy
import os, sys
import time, datetime
import ConfigParser

if not os.path.exists('./sinchoku.cfg'):
    print >> sys.stderr, "config file does not exist."
    sys.exit(1)

config = ConfigParser.SafeConfigParser()
config.read('./sinchoku.cfg')

CONSUMER_KEY = config.get("auth", "consumer_key")
CONSUMER_SECRET = config.get("auth", "consumer_secret")
ACCESS_TOKEN = config.get("auth", "access_token")
ACCESS_TOKEN_SECRET = config.get("auth", "access_token_secret")

# watch conf
INTERVAL = {
    "write": int(config.get("interval", "write"))*60,
    "sleep": int(config.get("interval", "sleep"))*60
}

STATE = {
    "stop": 0,
    "write": 1,
    "sleep": 2
}


def get_auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return auth


def tweet(s, api, me):
    date = datetime.datetime.now().strftime('%m/%d %H:%M:%S')
    api.update_status('@{0} {1} [{2}]'.format(me.screen_name, s, date))


if __name__ in '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, " ".join(["usage:", sys.argv[0], "<report.tex>"])
        sys.exit(1)
    fname = os.path.join(os.path.dirname(__file__), sys.argv[1])
    if not os.path.exists(fname):
        while not os.path.exists(fname):
            time.sleep(1)

    api = tweepy.API(get_auth())
    me = api.me()
    if '-q' not in sys.argv and '--quiet' not in sys.argv:
        tweet("レポートを書き始めたゾイ: (継続ノルマ:{0}分, 居眠り検知:{1}分)".format(INTERVAL["write"]/60, INTERVAL["sleep"]/60), api, me)

    prev = os.path.getmtime(fname)
    state = STATE["write"]
    sleep_cnt = 2
    while True:
        try:
            cur = os.path.getmtime(fname)
            d = int(time.time()) - prev
            if d > INTERVAL["sleep"]:
                if state == STATE["stop"]:
                    tweet("寝てるゾイ", api, me)
                    state = STATE["sleep"]
                elif state == STATE["sleep"] and d > INTERVAL["sleep"]*sleep_cnt:
                    tweet("まだ寝てるんですか？ｗ", api, me)
                    sleep_cnt += 1

            elif d > INTERVAL["write"]:
                if state == STATE["write"]:
                    tweet("レポートを書く手が止まったゾイ", api, me)
                    state = STATE["stop"]

            elif d <= INTERVAL["write"]:
                if state == STATE["sleep"]:
                    tweet("起きたゾイ", api, me)
                    state = STATE["write"]
                    sleep_cnt = 2
                elif state == STATE["stop"]:
                    tweet("レポートを再び書き始めたゾイ", api, me)
                    state = STATE["write"]
            prev = cur
                
            time.sleep(1)

        except KeyboardInterrupt:
            tweet("レポートを書くのをやめたゾイ", api, me)
            sys.exit(1)
