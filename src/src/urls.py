from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.views.generic import TemplateView
from django.views.generic import RedirectView

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'src.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^favicon\.gif$', RedirectView.as_view(url='/static/img/favicon.gif')),
    # main pages entry
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^index/$', TemplateView.as_view(template_name="index.html")),
)

# crawling route
urlpatterns += patterns('DBManagement.ajax',
    url(r'^clone/$', "clone_repsitory"), 
                       
)
