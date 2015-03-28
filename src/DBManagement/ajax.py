from django.http import HttpResponse, HttpRequest, JsonResponse, StreamingHttpResponse

# rendering html component templates
from django.template import Template, Context

# hight level api from system
# json data processing
import os, shutil, json
# processing new exec
from subprocess import call
'''
Created on 28 Mar, 2015

@author: wangyi
'''
# sub lib
from django.views.decorators.http import condition

# loc lib
from DBManagement.src.core.utils.executer import executer

# see http://stackoverflow.com/questions/2922874/how-to-stream-an-httpresponse-with-django
def clone_respository(request):
    if  request.method == 'GET':
        project_name = request.GET['name']
        request_urls = request.GET['urls']
        
        # data rep
        para = {}
        list = []
        
        if os.system('git clone %s ~/external/%s' % (request_urls, project_name)) != 0:
            return HttpResponse('repo existed or cannot create folder, try using /pull/<project_name> instead', 
                                status=410)
        if os.system('cd ~/external/%s && git push yiak master' % (project_name)) != 0:
            return HttpResponse('cannot deploy the new project. Test your deployment first dude!',
                                status=410)
        if os.system('cd ~/external/%s && git remote add yiak git@github.com:yiak/%s' % (project_name, project_name)):
            return HttpResponse('failed to add repository remote, please try again!', 
                                status=410)
        executable = executer(project_name) 
        # copy files to local and exec iterator
        return StreamingHttpResponse(next( executable ))


        
        

