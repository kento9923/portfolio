import requests
import tweepy
from termcolor import colored
from googleapiclient.discovery import build

#channelId
channelId = '＊＊＊＊＊'

# #TwitterAPIの連携キー
CONSUMER_KEY = '＊＊＊＊＊'
CONSUMER_SECRET = '＊＊＊＊＊'
ACCESS_TOKEN = '＊＊＊＊＊'
ACCESS_TOKEN_SECRET = '＊＊＊＊＊'


#YouTubeAPIの連携キー
DEVELOPER_KEY = '＊＊＊＊＊'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


#チャンネルIDから、そのチャンネル内で開催予定の生放送のビデオIDを取得
response_ch = youtube.search().list(
    part='snippet',
    # eventType='completed',
    eventType='upcoming',
    type='video',
    order='date',
    channelId=channelId
).execute()

Video_ID = response_ch['items'][0]['id']['videoId']
response = youtube.videos().list(
    part='snippet,liveStreamingDetails',
    id=Video_ID
).execute()

#ツイートする文章内容（生放送タイトル、放送開始時間、ひとことコメント、放送URL）を生成

stream_title = response['items'][0]['snippet']['title']#生放送タイトル

start_time_UTC = response['items'][0]['liveStreamingDetails']['scheduledStartTime']#放送開始時間（UTC）
start_time_JP = str(int(start_time_UTC[11:13])+9)#放送開始時間（日本時間）
start_time = start_time_UTC[:11]+start_time_JP+start_time_UTC[13:]#放送開始時間（月日時だけを取り出す）
start_time = start_time[5:16].replace('-','月').replace('T','日')#放送開始時間（1月1日のような表記にする）

description = response['items'][0]['snippet']['description']#放送の説明欄の文章取得
target1 = '''#スプラトゥーン3

'''
idx1 = description.find(target1) + len(target1)
target2 = '\n#ゲーム'
idx2 = description.find(target2)
comment = description[idx1:idx2]#ひとことコメント（放送の説明欄文章のうち、#スプラトゥーン3と#ゲームに囲まれた部分のみを取得

link = 'https://www.youtube.com/watch?v='+response['items'][0]['id']#放送URL

tweet_sentence = ('【放送予定】\nﾀｲﾄﾙ：'+stream_title+'\nｽﾀｰﾄ時刻：'+start_time+
      '\n🔹'+comment+'\n　　　　　⬇視聴URL⬇\n'+link)#ツイート文章

print(tweet_sentence)

thumbnail_url = response['items'][0]['snippet']['thumbnails']['maxres']['url']#サムネイルのURLを取得
file_name = 'thumbnail_today.jpg'

#ツイートを送信
#これが予約枠か判定
live_judge = response_ch['items'][0]['snippet']['liveBroadcastContent']
if live_judge == 'upcoming':
    with open(file_name, mode='wb') as f:#サムネイル画像を保存
        r = requests.get(thumbnail_url)
        f.write(r.content)
    print(colored('ツイートしました','green'))


    # Twitterオブジェクトの生成
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    #画像付きツイートを実行
    api.update_with_media(status = tweet_sentence, filename = 'thumbnail_today.jpg')

else:
    print(colored('失敗','red'))