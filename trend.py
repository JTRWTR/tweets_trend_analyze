#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tweepy
import sys
import time
from janome.tokenizer import Tokenizer
import tkinter
import functools,threading

from multiprocessing import Queue
import multiprocessing

root = tkinter.Tk()
root.title(u"TWEETS:POSITIVE AND NEGATIVE")
root.geometry("880x550")
root.configure(background='black')
Static1 = tkinter.Label(text=u'positive', foreground='#FFFFFF',background='black')
Static1.place(x=100, y=5)
Static2 = tkinter.Label(text=u'negative', foreground='#FFFFFF',background='black')
Static2.place(x=100, y=480)
Static3 = tkinter.Label(text="0", foreground='#FFFFFF',background='black')
Static3.place(x=180, y=510)
Static4 = tkinter.Label(text="96", foreground='#FFFFFF',background='black')
Static4.place(x=680, y=510)
canvas = tkinter.Canvas(root, width = 500, height = 500,background="#000000")
canvas.pack()


t = Tokenizer()

totalAVE=0
score=0
number=0
count=0
num_of_times=0
##########################################
tweet_count=100 #100
check_count=96 #96
interval=960 #900
##########################################
trend_tag_list=[]
nouns, verbs, adjs, advs = [], [], [], []
nounswords, verbswords, adjswords, advswords = [], [], [], []
nounspoint, verbspoint, adjspoint, advspoint = [], [], [], []
total_result=[]

def wrap_loop_thread(__sec_interval):
    def recieve_func(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            func(*args,**kwargs)
            thread_loop=threading.Timer(__sec_interval,functools.partial(wrapper,*args,**kwargs))
            thread_loop.start()
        return wrapper
    return recieve_func
########################################################################
#Twitter API
def get_oauth():
    consumer_key = 'jad3imHtiWpOCHoGYEX90L0Xp'
    consumer_secret = 'G5cjn9SrPlZ4tYujfQybodbV3R2JJR65XU3Hl9fWTpCSQJ0INg'
    access_key = '3033146437-ygVkg61FOLVLRz3lplfIHKojIHGUnU3ib1M61jU'
    access_secret = 'isalzsSIFUPpwxz3zxoNnnKOMTmYtgiAd3xfSlTfnQvxZ'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth
#########################################################################
#単語感情極性対応表の読み込み
def input_word_emotion():
    f = open('word_emotion.txt', 'r')
    for line in f:
        line = line.rstrip()
        x = line.split(':')
        if abs(float(x[3]))>0:	#ポイントの調整
            if x[2] == '名詞':
                nounswords.append(x[0])
                nounspoint.append(x[3])
            if x[2] == '動詞':
                verbswords.append(x[0])
                verbspoint.append(x[3])
            if x[2] == '形容詞':
                adjswords.append(x[0])
                adjspoint.append(x[3])
            if x[2] == '副詞':
                advswords.append(x[0])
                advspoint.append(x[3])
    f.close()
##########################################################################
#単語感情極性対応表に含む単語を抽出
def analyze(parts,words,point):
    global score, number
    for i in parts:
        cnt = 0
        for j in words:
            if i == j:
                #print (j, point[cnt])
                score += float(point[cnt])
                number += 1
            cnt += 1
##########################################################################
#文章を単語ごとに分解（JANOME）
def separete_word(text):
    global nouns, verbs, adjs, advs
    nouns, verbs, adjs, advs=[],[],[],[]
    for token in t.tokenize(text):
        partOfSpeech = token.part_of_speech.split(',')[0]
        if partOfSpeech == u'名詞':
            nouns.append(token.base_form)
        if partOfSpeech == u'動詞':
            verbs.append(token.base_form)
        if partOfSpeech == u'形容詞':
            adjs.append(token.base_form)
        if partOfSpeech == u'副詞':
            advs.append(token.base_form)
##########################################################################
#ツイートの取得
def get_tweets(api,tag):
    global score, number,nounspoint, verbspoint, adjspoint, advspoint, totalAVE,total_result
    print("-------------------------")
    print("-------------------------")
    print('【ハッシュタグ   ：  '+tag["name"]+'】')
    search_results = api.search(q=tag["name"]+" -rt", count=tweet_count)
    print("-------------------------")
    print("-------------------------")
    for i in search_results:
        print(i.user.name)
        print(i.text)
        separete_word(i.text)
        analyze(nouns,nounswords,nounspoint)
        analyze(verbs,verbswords,verbspoint)
        analyze(adjs,adjswords,adjspoint)
        analyze(advs,advswords,advspoint)
        if(number != 0):
            print("AVG="+str(score/number))
            totalAVE=totalAVE+score/number
        else:
            print("AVG="+str(score))
        score=0
        number=0
        print("-------------------------")
        print("-------------------------")
    if(len(search_results)>0):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  TAG-AVE : "+ str(totalAVE/len(search_results)))
        total_result.append(totalAVE/len(search_results))
    else:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  TAG-AVE : 0")
        total_result.append(0)
    totalAVE=0
##########################################################################
#トレンドキーワードを取得
def get_trends(api, woeid):
    trend = api.trends_place(woeid)[0]
    trends = trend['trends']
    print(u"場所：{0}".format(trend["locations"][0]["name"]))
    print(u"トレンド：")
    for i in range(len(trends)):
        print(u"\t{0}".format(trends[i]["name"]))
    return trends
##########################################################################
#点の描画
def draw(x,y,porn):
    if(porn=="p"):
        canvas.create_oval(x, y, x+5, y-5, fill = '#FF4D00',outline = '#FF4D00')
        canvas.pack()
    else:
        canvas.create_oval(x, y, x+5, y-5, fill = '#00B3FF',outline = '#00B3FF')
        canvas.pack()
##########################################################################
#各トレンドのAVGから点の座標を計算
def print_result():
    global trend_tag_list, total_result
    f = open('result.txt', 'a')
    f.write("【"+str(num_of_times)+":"+time.ctime()+"】")
    f.write("\n")
    for i in range(len(total_result)):
        if(float(total_result[i])>=-0.339941):
            r=trend_tag_list[i]["name"]+":"+str(total_result[i])+">[POSITIVE]"
            y=250-(total_result[i]+0.339941)*186
            draw(count*5,y,"p")
        else:
            r=trend_tag_list[i]["name"]+":"+str(total_result[i])+">[NEGATIVE]"
            y=250-(total_result[i]+0.339941)*378
            draw(count*5,y,"n")
        print(r)
        f.write(r)
        f.write("\n")
    f.write("\n")
    f.close()
##########################################################################
#実行
def run(api, woeid):
    try:
        start_time=time.time()
        global trend_tag_list, total_result, count

        if count<=96:
            count=count+1
        else:
            #count=1
            exit()
        total_result=[]
        trend_tag_list=get_trends(api, woeid)
        for i in trend_tag_list:
            get_tweets(api,i)
        print_result()
        finish_time=time.time()
        canvas.pack()
        canvas.update()
        root.quit()
        return int(finish_time-start_time)
        #t=threading.Timer(900,run,[api,woeid])
        #t.start()
    except tweepy.error.TweepError:
        print('TweepErrorエラーです。')
        exit()
##########################################################################
#結果を画像で保存
def saveImage():
	canvas.postscript(file = 'tweet_pn_result.ps')
##########################################################################

#INTERVAL_SEC_LOOP=900
#INTERVAL_SEC_LOOP=60
#@wrap_loop_thread(INTERVAL_SEC_LOOP)
def main():
    global count, num_of_times

    input_word_emotion()

    auth = get_oauth()
    api = tweepy.API(auth_handler=auth)
    if len(sys.argv) >= 2:
        woeid = int(sys.argv[1])
    else:
        woeid = 23424856 #日本
    while True:
        num_of_times=num_of_times+1
        process_time=run(api,woeid)
        if count==check_count:
            saveImage()
            count=0
            break
        if process_time<900 :
            time.sleep(interval-process_time)

    #t=threading.Thread(target=run,args=(api, woeid))
    #t.start()


if __name__ == '__main__':
    main()
    root.mainloop()
