# -*- coding: utf-8 -*-
'''
Created on 20 Oct, 2014

@author: wangyi
'''
# -- sys --
import contextlib
import queue
import re
import sys
import threading

import mysql.connector

__all__ = ['Connector', 'Database', 'DataNode'] 

CREATE = """
SHOW CREATE TABLE %(table_name)?s          
"""

INSERT_PATTERN = """

"""

# -- master - slaves architecture --
# --third party--
# --local dependency--
#from core.DAO.Log.LogManagement import logManager
#from core.utils.timmer import timmer, delta

class RunTimeErr(Exception):
    
    def __init__(self, string=None, name=None, err=None):
        self._err = mysql.connector.Error
        
        self._str = 'runtime error ' + self.name + ' : ' + err.__str__()
        
        print(self._str)
        
        Exception.__init__(self._str)
        

from DBManagement.src.core.utils.sql_parser import SQLparser

__author__   = "Wang Yi/Lei"
__credits__  = "all active authors in StackExchange, whom I learn a lot from"

# The prototype maintain global connector within an instance of the class life time
# As a part of data oriented work, data migration or converted from different servers are fairly frequent
# MySQL connector maintains a threads pool by default to create multiple connectors to a same database simutaneously  
class Connector(object):
    # default local machine DB config
    host     = "localhost"
    user     = "root"
    passwd   = "020139ERIyiak"
    db       = "ERI_Data_Storage"#"ERI_Statistic_Analysis"
    charset  = 'utf8'
    format   = 'json'
    # these mapping is used for general database querying, updating purpose, and should not be binded to models layer
    sqlMapping = {
        'alter' : {
            'create' : CREATE,
            'insert' : """
INSERT (INGNORE)? %(table_name)s VALUES \((\w+,?)*\)
            """,
            'alter'  : None,
            'delete' : None,
        },
        'query' : {
            '_?_table' : """
SELECT * FROM INFORMATION_SCHEMA.TABLES
WHERE table_schema = '%s' AND
    table_name = '%s'             
            """,
            
        }
                   
    }
    
    def __init__(self, **config): 
# following method discarded, might be consider a universe initial method:
        print('db start')
        # connection should lie in object domain, or simply put for enduring connection 
        if config == {}:     
            self.connection=mysql.connector.connect(host=self.host,  
                                                    user=self.user,  
                                                    passwd=self.passwd,  
                                                    db=self.db,
                                                    charset=self.charset
                                                    )
        else:
            self.db     = config['db']
            self.host   = config['host']
            self.user   = config['user']
            self.passwd = config['passwd']
            self.charset= config['charset']
            self.config = config
            
            if self.db != '':
                self.connection=mysql.connector.connect(**config)
            if self.db == '':
                pass


    def _instantiate(self):
        config = self.config.copy()
    
        if  self._instance == None:
            self._instance =  self.__class__(**config)

        return \
            self._instance
            

    def set_connector(self, db=''):
        
        raise NotImplementedError()
        
    def set_cursor(self):
        
        raise NotImplementedError()
    
    # cursor should lie in method domain
    # should consider transaction situations
    @contextlib.contextmanager
    def Cursor(self, **hint):
        # setup
        self.cursor = self.connection.cursor(**hint)

        try:
            yield
        # tear down
        except mysql.connector.Error as err:
            print(err)
            self.connection.rollback()
        finally:
            self.connection.commit()
            self.cursor.close()
            self.cursor=None    
    # This method can be safe
    def __del__(self):
        if  self.connection:
            print('db deleted')
            self.connection.close()   
            

# the basic database is used for querying or non-transaction based database interacting
# the database alwasy returns Json style data in python             
class Database(Connector): 
    
    def __init__(self, **config):
        super(Database, self).__init__(**config)
        
        self._input = queue.Queue()
        self._output = queue.Queue()
    
    def set_connector(self, db=''):
        self.db = db
        
        if  self.connection:
            self.connection.close()
        self.connection=mysql.connector.connect(host=self.host,  
                                                user=self.user,  
                                                passwd=self.passwd,  
                                                db=self.db,
                                                charset='utf8'
                                                )
        
    def basic(self, sql_str, callback, *args, **hint):
        
        sqls = SQLparser(sql_str, 
                         *args, 
                         **hint
                         ).begin()
        
        with self.Cursor():
            for sql in sqls:
                callback(sql)             
                
    def onQuery(self, sql):
        print('\t query begins')
        print( '\t\t ' + self.__str__() + '--' + self.cursor.__str__() )
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            
            if  self.format == 'json':
                self._output.put(self.json(results))
            else:
                self._output.put(results)
        except mysql.connector.Error as err:
            print( 'Error on query! ' + self.__str__() )
            raise(err)
        print('\t query ends')
    
    def onAlter(self, sql):
        sqls = sql.strip().split(';')
        for sql in sqls:
            if  sql != '':
                self.cursor.execute(sql)

## -- interface for user --    
    def query(self, sql, *args, **hint):
        
        self.basic(sql, self.onQuery, *args, **hint)

        list = []
        while True:
            try:
                list.append( self._output.get(block=False) )
            except queue.Empty:
                break
        
        if   list.__len__() == 1:
            return list[0]
        elif True:
            return list         
    
    def insert(self, sql, *args, **hint):
        if  hint != {}:
            # db sharding mode 
            try:        
                status = self.query(self.sqlMapping['query']['_?_table'], hint['db'], hint['table'])
                    
                if  not status:
                    self.onAlter(hint['create'], hint['table']) 
            except Exception as e:
                pass   
         
        self.basic(sql, self.onAlter, *args, **hint)       

#-- datatype mapping function--
    
    def json(self, results):
        print('\t\t transform begins')
        list = []
        for row in results:
            dict = {} 
            field = 0
            while True:
                try:
                    colname = self.cursor.description[field][0]
                    try:
                        dict[colname] = row[field].__unicode__()
                    except:
                        dict[colname] = row[field]
                    field = field +1
                except IndexError as e:
                    break
            list.append(dict)
        print('\t\t transform ends')
        return list
    
    def __str__(self):
        return "Database_Basic"   

    
class DataNode(Database, threading.Thread):

    def __init__(self, **config):
        Database.__init__(self, **config)
        
        self.config = config
        
        threading.Thread.__init__(self)     

        self.stoprequest = threading.Event()
        self.startloop = threading.Event()
        self.conlock = threading.Condition()
        
        self.cursor_setup = False
        self.cursor_close = True
        
        self.input_status = True
        self.daemon = True
        self.cursor = None
        
        self.counter= 0
        
        self.start()
    
    def addJob(self):
        self.counter += 1
    
    def rmvJob(self):
        self.counter -= 1
                
    def register(self, type_str, sql_str = None, *args, **hint):
        # open a cursor
        # enter in background sql event loop
        if  not self.startloop.isSet():
            self.startloop.set()
            
        if  self.input_status != True:
            return None
           
        self.addJob()
        
        sqls = SQLparser(
                         sql_str, 
                         *args, 
                         **hint
                         ).begin()
        
        for sql in sqls:
            # specif a transaction id, we will allocate a thread to execute it
            self._input.put( job(type_str, sql) )
    
    def execl(self, job):
        if  job.name == 'mysqlerror':
            print('\t\t master find an error event:' + job.data)
            raise(job.data)
        if  job.name == 'insert':
            self.onAlter(job.data)
            return
        if  job.name == 'query':
            self.onQuery(job.data)
            return
    
    def dispatch(self):
        
        while not self._input.empty():
            pass
        
        # deactivate loop                          # activate input 
        self.loop_set(), self.stoprequest.clear(), self.set_input_set()
        
        list = []
        while self.counter != 0:  
            self.rmvJob()
            # block calling thread until get a job
            list.append( self._output.get(block=True) )
            
        return list   

    def ioLoop(self):
                
        while not self.stoprequest.isSet():
            try:
                # sql event loop
                job = self._input.get(True, 0.05)
                # callback
                self.execl(job)
                
            except queue.Empty:
                continue
            except mysql.connector.Error as err:
                self.input_status = False
                self.stoprequest.set()
                print( 'runtime error ' + self.name + ' : ' + err.__str__() )
                raise mysql.connector.Error('master capture an err event:' + err )

    def run(self):
        
        while True:
            # wait for signal to start task-querying loop
            self.startloop.wait()
            
            with \
                self.Cursor(): # open cursor management
                # sql event loop
                self.ioLoop()

# logical implementation
    def loop_set(self):
        if  self.startloop.isSet():
            # set flag block the daemon thread
            self.startloop.clear()
        else:
            self.startloop.set()           
    
    def set_input_set(self):
        if  self.input_status == False:
            self.input_status =  True
            print('return unexpected!')
            return None
        else:
            self.input_status =  False
            
    def join(self, timeout=None):
        self.stoprequest.set()
        # block calling thread until the thread whose join is called is terminated   
        super(DataNode, self).join(timeout)
                     
class job(object):
    
    def __init__(self, name, data=None, call=None):
        self.name = name
        self.data = data
        self.call = call
 
Database = Database       