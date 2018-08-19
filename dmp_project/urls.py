"""dmp_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings

urlpatterns = [
    # admin moved to root
    path('', admin.site.urls),
]

admin.site.site_header = settings.MUSIC_PUBLISHER_SETTINGS.get(
    'publisher_name', 'Django Music Publisher')
admin.site.site_title = admin.site.site_header
admin.site.index_title = ''
admin.site.site_url = ''
