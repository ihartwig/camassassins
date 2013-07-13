from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'assassins.views.staticPage', name='assassins.views.staticPage'),
    # url(r'^assassins/', include('assassins.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin$', RedirectView.as_view(url='admin/')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^handleSms',
        'assassins_app.views.handleSms',
        name='assassins_app.views.handleSms'),

    url(r'^(?P<page_name>[\w%.]*)$', 'assassins.views.staticPage', name='assassins.views.staticPage'),

    url(r'^api/scoreboard$', 'assassins_app.views.scoreboard', name='assassins_app.scoreboard'),

    # url(r'^$',
    #     'assassins_app.views.handleStatic',
    #     name='assassins_app.views.handleStatic'),
)
