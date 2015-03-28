'''
Created on 29 Mar, 2015

@author: wangyi
'''
import time

def last():
    
    i = 0
    
    while True:
        yield str(i) + '\n'
        i = i+1
        
        time.sleep(0.2)

def main():
    # prepare
    iter = last()
    # run
    while True:
        print(next(iter))

if __name__ == "__main__":
    main()
    
