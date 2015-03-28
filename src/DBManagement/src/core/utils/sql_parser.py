# -*- coding: utf-8 -*-
'''
Created on 17 Oct, 2014

@author: wangyi
'''
import re

# work in the future

# 1. for two json version input, we will backup the lates. Currently can just support one nested data, it will be changed in the future 
# 2. deal with {:} substitution
# 3. support more data type examination
# date, datetime, time
DATE_PATTERN = re.compile("\b*(?P<date>\d{1,2}[-/:]\d{1,2}[-/:]\d{4})\b*")
TIME_PATTERN = re.compile("\b*(?P<time>\d{2}:\d{2}:\d{2})\b*")
DtTm_PATTERN = re.compile("\b*(?P<dttm>\d{1,2}[-/:]\d{1,2}[-/:]\d{4} *: *\d{0,2}:\d{0,2}:\d{0,2})\b*")

# keywords
KyVd_PATTERN = re.compile("\b*'(?P<key>[^']+)' *: *'?(?P<value>[^']+)'?\b*")

# values
VaLe_PATTERN = re.compile("\b*'?(?P<value>[^']+)'?\b*")

DELIMITER = (',')  

class SQLparser(object):
    
    def __init__(self, sql_str, *args_str, **hint_str):
        self.args = args_str
        self.hint  = hint_str
        self.sql_str = sql_str
                
        self.operate_stack = []
        self.operant_queue = []
        self.sql_clist  = []
        self.backup  = []
        
        self.operant_dict = {}
        self.operant_list = []
 
    def load_data(self, data_str):
        
        # timp term
        id = 0
        key = ""
        word = ""
        value = ""
        
        while True:
            # read all words
            try:
                # read a word, delimited by ','
                while True:
                    if  data_str[id] == ',':
                        id += 1
                        break
                    else:
                        word += data_str[id]
                        id +=1
                        
                # identify the datatype:
                
                # key value -- 
                match = re.search(KyVd_PATTERN, word)
                if match:
                    k = match.group('key')
                    v = match.group('value') 
                    self.operant_dict[k] = v
                    word = ""
                
                # normal value
                match = re.search(VaLe_PATTERN, word)
                if match:
                    v = match.group('value')
                    self.operant_list.append(v)
                    word = ""
            except IndexError as e:
                match = re.search(KyVd_PATTERN, word)
                if match:
                    k = match.group('key')
                    v = match.group('value') 
                    self.operant_dict[k] = v
                    word = ""
                
                match = re.search(VaLe_PATTERN, word)
                if match:
                    v = match.group('value')
                    self.operant_list.append(v)
                    word = ""                
                
                break  

    def stackloop(self, sign_in, sign_out, data_str):
        # counter
        i = 1
        
        # word
        words  = ''
        
        # no stack dismatch handling needed 
        while True:
            try:
                if   data_str[i] == sign_out:
                    self.operate_stack.pop()
                    if   self.operate_stack.__len__() != 0:
                        words += data_str[i]
                    elif True:
                        break
                elif data_str[i] == sign_in:
                    self.operate_stack.append(sign_in)
                    words += data_str[i]
                elif True:
                    words += data_str[i]
                i += 1
            except IndexError as e:
                break
        return i + 1, words

    def sqlParser(self, sql):
        s = False
        j = 0
         
        while True:
            try:
                if   sql[j] == '%' and sql[j + 1] == 's':
                    pre = sql[:j]
                    
                    try:
                        value = self.operant_list.pop()
                    except:
                        raise TypeError('not all arguments converted during string formatting')
                    
                    succ = sql[j + 2:]
                    sql = pre + value + succ#operant_stack.pop() + succ
                    
                    j = j - 1 + value.__len__() + 1
                    
                elif sql[j] == '%' and sql[j + 1] == '(':
                    pre = sql[:j]
                    
                    key = ""
                    k = 2
                    while sql[j + k] != ')':
                        key += sql[j + k]
                        k += 1
    
                    try:
                        value = self.operant_dict.pop(key)
                    except:
                        if  self.hint != {}:
                            try:
                                if  self.hint['auto_debug'] == False:
                                    s = True
                                    j = j + 1
                                    continue
                            except Exception as e:
                                pass 
                        
                        # error - 1
                        # raise TypeError('not all arguments converted during string formatting')
                        # try list
                        try:
                            value = self.operant_list.pop()
                        except:
                            # cannot handle error - 1
                            raise TypeError('not all arguments converted during string formatting')
                        
                    succ = sql[j + k + 2:]
                    sql = pre + value + succ
                    
                    j = j - 1 + value.__len__()  + 1    
    
                elif sql[j] == '{':
                    # this version of string substitution is under development
                    pre = sql[:j]
                    
                    key = ""
                    k = 1
                    while sql[j + k] != '}':
                        key += sql[j + k]
                        k += 1
                        
                    # To Do: produce value
                    value = None
                                               
                    succ = sql[j + k + 1:]
                    sql = pre + value + succ
                    j = j - 1 + value.__len__() + 1
                    
                elif True:
                    j = j + 1
                
            except IndexError as e:
                # since this layer just process one row data, so
                if  s == True:
                    e = TypeError('not all arguments converted during string formatting')
                    e.sql = sql
                    raise(e) 
                
                self.sql_clist.append(sql)
                break 
            except TypeError as e:
                e.sql = sql
                raise(e)   

    # non-recursive version, thread stack safe
    def dataParser2(self, data_str, sql_str):
        stack = []
        
        stack.append( (data_str, sql_str) )
        
        while True:
            try:
                data_str, sql_str = stack.pop(0)
                
                if   data_str == '':
                    pass   
                
                elif data_str[0] == '[':
                    self.operate_stack.append('[')         
        
                    index, words = self.stackloop('[', ']', data_str)
                    
                    # load one row data: words = 'x,y'        
                    stack.append( (words, sql_str) )
                    stack.append( (data_str[index:], sql_str) )
                               
                elif data_str[0] == '{':
                    self.operate_stack.append('{')
        
                    # To do get all data splited by ',' between '{ }' into stack             
                    index, words = self.stackloop('{', '}', data_str)
                    
                    stack.append( (words, sql_str) )
                    stack.append( (data_str[index:], sql_str) )
                
                elif data_str[0] == ',' or data_str[0] == ' ' or data_str[0] == '\t':
                    stack.append( (data_str[1:], sql_str) )
                
                elif True:
                    self.load_data(data_str)
                    self.sqlParser(sql_str)                
                
            except IndexError as e:
                break
            except TypeError as e:
                raise(e)

    # main entry
    # recursive version, not thread stack safe if the number of records is too large
    def dataParser(self, data_str, sql_str):
    
        try:
            if   data_str == '':
                pass   
            
            elif data_str[0] == '[':
                self.operate_stack.append('[')         
    
                index, words = self.stackloop('[', ']', data_str)
                
                # load one row data: words = 'x,y'        
                self.dataParser(words, sql_str)
                self.dataParser(data_str[index:], sql_str)
                           
            elif data_str[0] == '{':
                self.operate_stack.append('{')
    
                # To do get all data splited by ',' between '{ }' into stack             
                index, words = self.stackloop('{', '}', data_str)
                
                self.dataParser(words, sql_str)
                self.dataParser(data_str[index:], sql_str)
            
            elif data_str[0] == ',' or data_str[0] == ' ' or data_str[0] == '\t':
                self.dataParser(data_str[1:], sql_str)
            
            elif True:
                self.load_data(data_str)
                self.sqlParser(sql_str)            
        except IndexError as e:
            pass
        except TypeError as e:
            raise(e)
    
    # main loop    
    def begin(self):
        # in the future I wil change it to str dump version
        if  self.args == ():
            return [self.sql_str]
        if  self.hint == {}:
            # examine mode
            pass
        for data in self.args:
            try:
                self.dataParser2(data.__str__(), self.sql_str)
            except TypeError as e:
                # for two json version input, we will backup the latest version by non-nested data substitution 
                self.backup.append(self.sql_str)
                self.sql_str = e.sql
                
        return  self.sql_clist

