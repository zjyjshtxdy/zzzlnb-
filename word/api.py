# -*- coding:utf-8 -*
from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app, supports_credentials=True, origins="*")

import os
import json
import sqlite3 as sq
import random
info = None
cwd = os.getcwd()
bookName = None
wkdir = None
port = None
word_list = []
def ini_prog():
    global bookName, wkdir, port, info
    if os.path.exists('config.json'):
        pass
    else:
        print('config not found')
        print(f'cwd being {cwd}')
        print('exist')
        return
    with open('config.json','r',encoding = "utf-8") as f:
        config = f.read()
    config = json.loads(config)
    bookName = config['bookName']
    wkdir = config['wkdir']
    port = config['port']
    with open(bookName+'.json', 'r',encoding = "utf-8") as f:
        info = f.readlines()
    if os.path.exists(wkdir):
        pass
    else:
        os.mkdir(wkdir)
        ini_book(bookName)
def ini_book(bookn):
    con = sq.connect(os.path.join(wkdir, 'mydb.db'))
    cursorObj = con.cursor()
    global bookName
    bookName = bookn
    bookS = None
    with open(bookName+'.json', 'r',encoding = "utf-8" ) as f:
        bookS = f.readlines()
    cmd = f'SELECT * FROM sqlite_master WHERE type="table" AND name = "{bookName}";'
    cursorObj.execute(cmd)
    if (len(cursorObj.fetchall())>0):
        cmd = f'drop table {bookName}'
        cursorObj.execute(cmd)
    cmd = f'create table {bookName}(rank int, memorized int, familiar int, visited int)'
    cursorObj.execute(cmd)
    i = 0
    for l in bookS:
        wd = json.loads(l)
        rank = wd['wordRank']
        try:
            usphone = wd['content']['word']['content']['usphone']
        except:
            usphone = ''
            i += 1
        cmd = f'insert into {bookName} values({rank}, 0, 0, 0)'
        cursorObj.execute(cmd)
    con.commit()
def handle_start(num):
    con = sq.connect(os.path.join(wkdir, 'mydb.db'))
    cursorObj = con.cursor()
    ans = {}
    global today_num, word_list
    today_num = num
    new_words = []
    old_words = []
    cmd = f'select * from {bookName} where visited = 0'
    cursorObj.execute(cmd)
    cnt = cursorObj.fetchall()
    random.shuffle(cnt)
    thLen = min(len(cnt), num)
    print(thLen)
    for i in range(thLen):
        new_words.append(list(cnt[i]))
    cmd = f'select * from {bookName} where visited = 1 and memorized = 0'
    cursorObj.execute(cmd)
    cnt = cursorObj.fetchall()
    random.shuffle(cnt)
    for i in cnt:
        old_words.append(list(i))
    word_list = new_words+old_words
    ans['left'] = len(word_list)
    con.commit()
    return ans
def handle_query():
    ans = {}
    if (len(word_list) == 0):
        ans['left'] = 0
    else:
        ans['left'] = len(word_list) 
        ans['index'] = random.randrange(0, len(word_list))
        ans['word'] = info[ans['index']-1]
        return ans
def set_db(line):
    con = sq.connect(os.path.join(wkdir, 'mydb.db'))
    cursorObj = con.cursor()
    cmd = f'update {bookName} set memorized={line[1]} and familiar={line[2]} and visited=1 where rank={line[0]}'
    cursorObj.execute(cmd)
    con.commit()
def handle_answer(index, recog):
    wd = word_list[index]
    if recog:
        if wd[3] == 0:
            wd[1] = 1
        else:
            wd[2] += 1
            if wd[2] > 2:
                wd[1] = 1
        word_list.pop(index)
    else:
        wd[2] = 0
    set_db(wd)

@app.route('/start',methods=['GET','POST'])
def service_start():
    num = request.form['num']
    print(f'start ask {num}')
    ans = handle_start(int(num))
    return json.dumps(ans)

@app.route('/query',methods=['GET','POST'])
def service_query():
    ans = handle_query()
    return json.dumps(ans)

@app.route('/ans',methods=['GET','POST'])
def service_ans():
    index = request.form['index']
    index = int(index)
    recog = request.form['recog']
    if (recog == '1'):
        recog = True
    else:
        recog = False
    handle_answer(index, recog)
    return 'ok'
ini_prog()
app.run(port=port, debug=True, host='0.0.0.0')