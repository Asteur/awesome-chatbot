#!/usr/bin/python3

import codecs
import sqlite3
import os
from datetime import datetime

timeframe = 'input'
sql_transaction = []

shift_and_repeat = False
test_on_screen = False

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS parent_reply(parent_id TEXT PRIMARY KEY, comment_id TEXT UNIQUE, parent TEXT, comment TEXT, subreddit TEXT, unix INT, score INT)")

def format_data(data):
    #data = str(data)

    data2 = data.replace('\n',' newlinechar ').replace('\r',' newlinechar ').replace('"',"'")
    #data = data[:]
    #data = data.encode('utf8')
    return data2

def transaction_bldr(sql , force=False):
    global sql_transaction
    if not force: sql_transaction.append(sql)
    if len(sql_transaction) > 1000 or force:
        c.execute('BEGIN TRANSACTION')
        for s in sql_transaction:
            try:
                c.execute(s)
            except:
                pass
        connection.commit()
        sql_transaction = []

def sql_insert_replace_comment(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """UPDATE parent_reply SET parent_id = ?, comment_id = ?, parent = ?, comment = ?, subreddit = ?, unix = ?, score = ? WHERE parent_id =?;""".format(parentid, commentid, parent, comment, subreddit, int(time), score, parentid)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))

def sql_insert_has_parent(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(parentid, commentid, parent, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))

def sql_insert_no_parent(commentid,parentid,comment,subreddit,time,score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}",{},{});""".format(parentid, commentid, comment, subreddit, int(time), score)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))

def sql_insert_complete(commentid,parentid,parent,comment,subreddit,time,score):
    try:
        sql = """INSERT INTO parent_reply (parent_id, comment_id,parent, comment, subreddit, unix, score) VALUES ("{}","{}","{}","{}","{}",{},{});""".format(parentid, commentid,parent, comment, subreddit, int(time), 5)
        transaction_bldr(sql)
    except Exception as e:
        print('s0 insertion',str(e))


def acceptable(data):
    return True
    '''
    if len(data.split(' ')) > 500 or len(data) < 1:
        return False
    elif len(data) > 1000:
        return False
    elif data == '[deleted]':
        return False
    elif data == '[removed]':
        return False
    else:
        return True
    '''

def find_parent(pid):
    try:
        sql = "SELECT comment FROM parent_reply WHERE comment_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    except Exception as e:
        #print(str(e))
        return False

def find_existing_score(pid):
    try:
        sql = "SELECT score FROM parent_reply WHERE parent_id = '{}' LIMIT 1".format(pid)
        c.execute(sql)
        result = c.fetchone()
        if result != None:
            return result[0]
        else: return False
    except Exception as e:
        #print(str(e))
        return False
    
if __name__ == '__main__':
    create_table()
    row_counter = 0
    paired_rows = 0
    txtname = 'movie_lines'
    with codecs.open('{}.txt'.format(txtname), 'rb',encoding='cp1252' ,buffering=1000) as z: # cp1252
        f = z.read()
        bucket = ''
        row = ''
        rownext = ''
        row_out = ''
        num = 0
        body = ''
        reply = ''
        name = ''
        done = False
        done_counter = 0
        comment_id = ''
        parent_id = ''
        comment_id_name = ''
        
        for j in range(len(f)): 
        
            
            if str(f[j]) != '\n' and str(f[j]) != '\r':
                bucket += f[j]
                done = False
                #done_counter +=1
            else:
                #print('return')
                row = bucket[:]
                bucket = ''
                done = True
                row_counter += 1
                parent_id = num 
            
            
            if done:
                pos = 0
                pos_name = 0
                row_in = row.split()
                for i in range(len(row_in)):
                    if row_in[i].endswith('+'):
                        pos = i + 1
                        if i - 1 >= 0: pos_name = i - 1
                    pass
                row_out = ' '.join(row_in[pos:])
                name = row_in[pos_name].lower()
            
                comment_id = 'name-'+str(num)  
                commentnext_id = 'reply-'+ str(num+1)
                comment_id_name = comment_id + ' ' + str(row_counter)

            created_utc = row_counter
            score = 5  
            
            
            subreddit = 0  
            parent_data = False  

            if done and row_counter % 256 == 0:
                text = "i am {} .".format(name)
                text2 = "this is {} .".format(name)
                sql_insert_complete(comment_id_name, parent_id, text, text2, subreddit, created_utc, score)
                if test_on_screen:
                    print(text, row_counter)
                    #exit()
                pass
            
            if done : #and reply == '':
                reply = str(format_data(row_out))

            
                if body == '': body = reply[:]
            
                #if done: #acceptable(body) and acceptable(reply) and done :
                done = False
                
                if row_counter % 2 == 0 or  shift_and_repeat:
                    if test_on_screen and False:
                        print(body, '-body-',row_counter)
                        print(reply,'-reply-',row_counter)
                        print(name, '-name-\n', row_counter)
                
                    if True:
                        sql_insert_complete(comment_id,parent_id,body,reply,subreddit,created_utc,score)
                        done_counter += 1

                    body = '' #reply[:]

                if row_counter % 100000 == 0:
                    print('Total Rows Read: {}, Paired Rows: {}, Time: {}'.format(row_counter, paired_rows, str(datetime.now())))

                #if done:
                num += 1

        transaction_bldr('', force=True)

    os.system("mv input.db raw/input_movie.db")