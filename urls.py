from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, databrowse
from foodtruck.models import *


admin.autodiscover()


urlpatterns = patterns('foodtruck.views',
	(r'^$','food_truck'),
	(r'^neighborhood/(?P<hood>\d+)/$', 'hood_truck',),
    (r'^admin/', include(admin.site.urls)),
    (r'^databrowse/(.*)', databrowse.site.root),
)
