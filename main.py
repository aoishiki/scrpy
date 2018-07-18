# coding=utf-8
import os
import glob
import time
from datetime import datetime
from auth import api,dbx
import requests
import shutil

# define
log_file = "./log.txt"
upload_folder = './upload/'
ftype = ['.jpg','.jpeg','.png','.gif']

def download(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

def get_img_url(tw_d) :
    return tw_d["media"][0]["media_url_https"]

def get_db_folder(path) :
    for entry in dbx.files_list_folder(path).entries:
        print(entry.name)

def get_img_name(url) :
    word = "/media/"
    wlen = len(word)
    w_location = url.find(word)
    if w_location != -1 :
        return url[w_location+wlen:]
    else :
        return 0

def check_log(name) :
    if name != 0 :
        with open(log_file,"r") as log :
            # log file と比較
            for uploaded_file in  log.readlines():
                if name == uploaded_file.strip() :
                    return False
        # log fileに書き込む
        with open(log_file,"a+") as log :    
            log.writelines(name+'\n')
        return True
    else :
        return False

def get_img(tweet) :
    try:
        tw_data = tweet["entities"]
        if "media" in tw_data:
            url = get_img_url(tw_data)
            name = get_img_name(url)
            if  check_log(name) :
                print(url)
                download(url,name)
                try :
                    shutil.move("./"+name,upload_folder)
                except:
                    #clean local dir
                    os.remove("./"+name)
    except:
        pass

# path :: dir -> upload all image file in dir
#      :: file name -> upload image file 
def upload_img(path) :
    for ft in ftype :
        files = glob.glob(path+'*'+ft)
        for upfile in files :
            name = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
            f = open(upfile,'rb')
            dbx.files_upload(f.read(),'/image/'+name+ft)
            f.close()
            os.remove(upfile)
            
request_time = [x for x in range(59) if x%3 == 0]

print("scrpy : Hello ...")
print("state : stand-by")

def time_flag(time) :
    for req_t in request_time :
        if time == req_t:
            return True
    return False

while 1:
    t = datetime.now().minute
    if time_flag(t) :
        try :
            for tweet in api.statuses.home_timeline() :
                get_img(tweet)
            upload_img(upload_folder)
            print("message : "+datetime.now().strftime("%Y-%m-%d %H.%M.%S")+"に処理が実行されました")
            time.sleep(60)
        except :
            print("message : "+datetime.now().strftime("%Y-%m-%d %H.%M.%S")+"にエラーが発生しました")
            time.sleep(600)