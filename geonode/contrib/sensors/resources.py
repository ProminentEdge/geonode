from django.conf import settings

from tastypie.resources import ModelResource
from tastypie import fields

from geonode.api.resourcebase_api import  CommonMetaApi
from geonode.contrib.sensors.models import SensorServer
from geonode.contrib.sensors.models import Sensor

class SensorServerResource(ModelResource):
    class Meta:
        queryset = SensorServer.objects.all()
        resource_name = 'sensorservers'

class SensorResource(ModelResource):

    """Sensors API"""
    server = fields.ForeignKey(SensorServerResource, 'server', full=True)

    class Meta(CommonMetaApi):
        queryset = Sensor.objects.distinct().order_by('-date')
        if settings.RESOURCE_PUBLISHING:
            queryset = queryset.filter(is_published=True)
        resource_name = 'sensors'

