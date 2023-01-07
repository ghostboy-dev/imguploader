from os.path import exists
import time
import sqlite3
import os
import os
from threading import Thread
import requests
import datetime
import random
import secrets
import string


import sys
sys.dont_write_bytecode = True

#configs
domain = ''
delurl = ''
errorlogurl = ''
master_key = ''
website_icon = ''
website_name = ''
embed_description = ''
cleaner_time = datetime.timedelta(days=21)


def dbmaker():
    if not exists('keys.db'):
        f = open('keys.db', 'w')
        f.close()
        time.sleep(1)
        con = sqlite3.connect('keys.db')
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS keys (key TEXT, dcid INTEGER, customtext TEXT, color TEXT, webhook TEXT)""")

        cur.execute("CREATE TABLE IF NOT EXISTS masterkey (key TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS keyupload (key TEXT, imgname TEXT)")
        con.commit()
    else:
        con = sqlite3.connect('keys.db')
        cur = con.cursor()


    getmaster = cur.execute(f"SELECT key FROM masterkey").fetchall()
    if str(getmaster) == '[]':
        cur.execute(f"INSERT INTO masterkey VALUES ('{master_key}')")
        con.commit()

    return cur, con



def getstats(stsize):
    imagekb = stsize / 1000
    if imagekb > 1000:
        imagemb = imagekb / 1000
        if imagemb > 1000:
            imagegb = imagemb / 1000
            return 'GB', imagegb
        else:
            return 'MB', imagemb
    else:
        return 'KB', imagekb

class Helper():
    @classmethod
    def unix_converter(cls, time_to_convert):
        time_converted = datetime.datetime.strptime(time_to_convert, '%d.%m.%Y | %H:%M')
        time_converted = time_converted - datetime.timedelta(hours=1)
        time_converted = str(time_converted.timestamp()).split('.')[0]
        
        time_converted = f'<t:{time_converted}:R>'
        return time_converted


class Verfiy():
    @classmethod
    def verifydc(cls, dc):
        getsql = dbmaker()
        cur = getsql[0]
        con = getsql[1]
        getmasterkey = cur.execute(f"SELECT key FROM keys WHERE dcid=('{str(dc)}')").fetchall()
        con.close()
        if not str(getmasterkey) != '[]':
            invalidarg = {
                "Error": "You must have an dcid in the request"
            }
            con.close()
            restext = invalidarg, 400
            return True, restext
        else:
            con.close()
            resttext = "valid dcid"
            return False, resttext
        
    
    @classmethod
    def verifykey(cls, key):
        getsql = dbmaker()
        cur = getsql[0]
        con = getsql[1]
        getverex = cur.execute(f"SELECT key FROM keys WHERE key=('{str(key)}')").fetchall()
        con.close()
        if str(getverex) == '[]':
            invalidarg = {
                "Error": "key not found"
            }
            restext = invalidarg, 400
            return True, restext
        else:
            resttext = "valid key"
            return False, resttext

    @classmethod
    def verifymasterkey(cls, masterkey):
        getsql = dbmaker()
        cur = getsql[0]
        con = getsql[1]
        getmasterkey = cur.execute(f"SELECT key FROM masterkey WHERE key=('{str(masterkey)}')").fetchall()
        con.close()
        if not str(getmasterkey) != '[]':
            invalidarg = {
                "Error": "You must have an valid masterkey in the request"
            }
            resttext = invalidarg, 400
            return True, resttext
        else:
            resttext = "valid masterkey"
            return False, resttext



class Configparser():
    def showconfig(getconfig):
        if str(getconfig) == '[]':
            res = {
                "Error": "The user has key"
            }
            return res, 400


        config = {
            "Config": f"config fetched from <@{getconfig[0][0]}> ({getconfig[0][0]})",
            "Key": getconfig[0][1],
            "DC": getconfig[0][2],
            "Customtext": getconfig[0][3],
            "Color": getconfig[0][4],
            "Webhook": getconfig[0][5]
        }
        return config

        

def filecleaner():
    for imgmame in os.listdir('templates/images/'):
        imgstats = os.stat(f'templates/images/{imgmame}')
        filesize = getstats(imgstats.st_size)
        filetime = datetime.datetime.fromtimestamp(imgstats.st_ctime, datetime.timezone(datetime.timedelta(hours=1))) 
        weeksb = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))) - cleaner_time

        imgtexttime = filetime.strftime('%d-%m-%Y | %H:%M')
        imgtext = f'{imgtexttime} | {filesize[1]} ({filesize[0]})'
        
        try:
            if filetime <= weeksb:
                getsql = dbmaker()
                cur = getsql[0]
                con = getsql[1]
                delitem = str(imgmame).split('.')[0]
                cur.execute(f"DELETE FROM keyupload WHERE imgname=('{delitem}')")                
                con.commit()
                con.close()
                
                os.remove(f'templates/images/{imgmame}')
                Thread(target=dellog, args=(delurl, imgmame, imgtext)).start()
        except:
            pass
        
def passwordmaker(size):
    characters = string.ascii_uppercase + string.digits + string.ascii_lowercase + '!#$%&*+-/:;<=>?@[]^_{|}~'
    getpasswd =  ''.join(secrets.choice(characters) for x in range(size))
    return getpasswd

def dellog(webhookurl, filename, filestats):
    embeds = {
        "title": "Image auto delete system",
        "color": 16724016,
        "footer": {
            "text": "Image uplaoder",
            "icon_url": "https://ghostboy.dev/assets/darkman.gif"
        },
        "fields": [
            {
                "name": f"Image ({filename}) stats",
                "value": filestats
            },
        ],
    }
    

    data = {
        "username": "Api log",
        "avatar_url": "https://ghostboy.dev/assets/darkman.gif",
        "embeds": [
            embeds
        ],
    }
    requests.post(url=webhookurl, json=data)


def log(connectip, api_key, webhookurl, imgtext, dcid, filename):
    if str(webhookurl) == 'No':
        return

    time_to_convert = str(imgtext)[0:18]
    set_time_stamp = Helper.unix_converter(time_to_convert=str(time_to_convert))
    rest_time_stamp = str(imgtext)[21:]
    splittet_time_part = f'{set_time_stamp} | {rest_time_stamp}'
    
    embeds = {
        "title": "Image system",
        "color": 16724016,
        "footer": {
            "text": "Image uplaoder",
            "icon_url": "https://ghostboy.dev/assets/darkman.gif"
        },
        "fields": [
            {
                "name": "Image uploaded information",
                "value": f'Upload IP: ||{connectip}||\nApi_key: ||{api_key}||\nDC: {dcid}'
            },
            {
                "name": "Image stats",
                "value": f'File: {filename}\nStats: {splittet_time_part}'
            }

        ],
        "image": {
            "url": f"https://{domain}/images/{filename}"
        }
    }
    

    data = {
        "username": "Api log",
        "avatar_url": "https://ghostboy.dev/assets/darkman.gif",
        "embeds": [
            embeds
        ],
    }
    requests.post(url=webhookurl, json=data)



def errrorpost(reqip, error):
    embeds = {
        "title": "Image error log system",
        "color": 16724016,
        "footer": {
            "text": "Image error log system",
            "icon_url": "https://ghostboy.dev/assets/darkman.gif"
        },
        "fields": [
            {
                "name": "Image error log",
                "value": f'Req IP: ||{reqip}||\nError: ```{error}```'
            }
        ]
    }
    data = {
        "username": "Api log",
        "avatar_url": "https://ghostboy.dev/assets/darkman.gif",
        "embeds": [
            embeds
        ],
    }
    try:
        requests.post(url=errorlogurl, json=data)
    except:
        pass