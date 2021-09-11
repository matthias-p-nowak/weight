import atexit
import datetime
import logging
import os.path
import sqlite3
import time
from tabnanny import check

import completer
import config

# noinspection PyTypeChecker
dbCon: sqlite3.Connection = None


def closeDataDb():
    global dbCon
    logging.info('closing db')
    dbCon.close()


schemaStmts = [
    'CREATE TABLE dbv ( version INTEGER NOT NULL)',
    'CREATE TABLE weight ( t DATETIME DEFAULT CURRENT_TIMESTAMP primary key, w real)',
    'insert into dbv values(1)'
]
updateStmts = []


def checkData():
    global dbCon
    if dbCon is None:
        dbFnName = config.getConfig('db', os.path.expanduser('~/.weight/db.sql3'))
        logging.info('opening database connection ' + dbFnName)
        if not os.path.exists(dbFnName):
            logging.warning('need to create file ' + dbFnName)
            dn = os.path.dirname(dbFnName)
            if not os.path.exists(dn):
                os.makedirs(dn)
        try:
            dbCon = sqlite3.connect(dbFnName)
            atexit.register(closeDataDb)
            version = 0
            try:
                for r in dbCon.execute('select * from dbv'):
                    if version < r[0]:
                        version = r[0]
            except:
                logging.info('no versions found')
            if version == 0:
                logging.info("creating db from scratch")
                for stmt in schemaStmts:
                    dbCon.execute(stmt)
            dbCon.commit()
        except Exception as e:
            print('no database: ',e)
            exit(2)
    return dbCon


def addWeight(args: list[str]):
    if len(args) > 0:
        con = checkData()
        con.execute('insert into weight(w) values(?)', (args[0],))
        con.commit()
    else:
        print('use: add <weight>')


def listWeights(args):
    con = checkData()
    rows=con.execute('select t,w from weight').fetchall()
    num = config.getConfig('data.listLast', 7)
    num = int(num)
    rows = rows[-num:]
    for row in rows:
        print('{}:{:>7.1f}'.format(row[0], row[1]))


def deleteItem(args):
    con = checkData()
    if con is None:
        print('no database')
        exit(2)
    rows = con.execute('select t,w from weight').fetchall()
    num = config.getConfig('data.listLast', 7)
    num = int(num)
    rows = rows[-num:]
    for i in range(len(rows)):
        print('{:>3d}) {}:{:>7.1f}'.format(i, rows[i][0], rows[i][1]))
    pos=input('delete item >')
    if pos.isnumeric():
        pos=int(pos)
        con.execute('delete from weight where t=?',(rows[pos][0],))
        con.commit()

def keepItems(args):
    con=checkData()
    kd=input('specify number of days >')
    if kd.isnumeric():
        kd=int(kd)
        dt=datetime.datetime.now()
        td=datetime.timedelta(days=kd)
        dt=dt-td
        print('deleting items older than {}'.format(dt))
        con.execute('delete from weight where t < ?',(dt,))
        con.commit()


def init_data():
    logging.debug('initializing data module')
    dataOpt = completer.ComplOption('data')
    completer.rootCompleter.add(dataOpt)
    addOpt = completer.ComplOption('add', final=True)
    addOpt.exec = addWeight
    dataOpt.add(addOpt)
    listOpt = completer.ComplOption('list', final=True)
    listOpt.exec = listWeights
    dataOpt.add(listOpt)
    delOpt = completer.ComplOption('delete', final=True)
    delOpt.exec = deleteItem
    dataOpt.add(delOpt)
    keepOpt=completer.ComplOption('keep',final=True)
    keepOpt.exec=keepItems
    dataOpt.add(keepOpt)
