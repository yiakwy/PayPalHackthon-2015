'''
Created on 28 Mar, 2015

@author: wangyi

All rights reserved ^.^
'''
# get runnning results
# in python 2.x (x <= 6), using commands but it is deprecated in python 3.x
# refer to http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
import subprocess, sys, os

# files path config
pwd = os.path.dirname( os.path.realpath(__file__) )

class ProcessException(Exception):
  def __init__(self, value):
    self.parameter = value

  def __str__(self):
    return repr(self.parameter)

class executer(object):
    
    def __init__(self):
        pass
    
    class excecuterItor(object):
        
        def __init__(self, iexecuter):
            pass
    
    def fire(self, filename, method="python"):
        # to do: file processing
        print(pwd)
        
        command = self.filename2command(filename, method)
        
        try:
            return next(self.streaming_response(command))
        except StopIteration:
            raise StopIteration()
    # make it a generator
    __next__ = fire
    
    # content generator
    def streaming_response(self, command):
        # open a subprocess
        process = subprocess.Popen(command, 
                                   shell=True, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT)
        
        # run the command line
        for line in iter(process.stdout.readline, b""):
            sys.stdout.write(line);
            sys.stdout.flush();
            # for live resposne processing
            yield line
            
    def filename2command(self, filename):
        args = ["python3 ", pwd + " ", filename]
        
        # return commands generated
        return ''.join(args)
        
        
