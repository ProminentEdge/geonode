# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import patterns, url
from django.conf import settings
from django.views.generic import TemplateView
from geonode.api.urls import api
from geonode.contrib.sensors.resources import SensorServerResource, SensorResource

api.register(SensorServerResource())
api.register(SensorResource())

js_info_dict = {
    'packages': ('geonode.contrib.sensors',),
}

urlpatterns = patterns(
    'geonode.contrib.sensors.views',
    url(r'^$', TemplateView.as_view(template_name='sensors_list.html'), name='sensors_browse'),
    url(r'^add$', 'sensors_add', name='sensors_add'),
    url(r'^(?P<sensor_id>[^/]*)$', 'sensor_detail', name="sensor_detail"),
    #url(r'^add/connect$', 'sensors_add_connect', name='sensors_add_connect'),
)