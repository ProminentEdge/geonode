import uuid
import logging
import json

from datetime import datetime


from django.db import models
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage

from geonode.base.models import ResourceBase, ResourceBaseManager, resourcebase_post_save
from geonode.maps.models import Map
from geonode.people.utils import get_valid_user
from agon_ratings.models import OverallRating
from geonode.utils import check_shp_columnnames
from geonode.security.models import remove_object_permissions
from django.utils.timezone import now

logger = logging.getLogger("geonode.sensors.models")


class SensorServer(models.Model):
    url = models.CharField(max_length=512, unique=True)


class Sensor(ResourceBase):
    server = models.ForeignKey(SensorServer)
    name = models.CharField(max_length=64)
    offering_id = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    start_time = models.CharField(max_length=32)
    end_time = models.CharField(max_length=32)
    user_start_time = models.DateTimeField()
    user_end_time = models.DateTimeField()

    observable_props = models.CharField(max_length=512)
    selected_observable_props = models.CharField(max_length=512,null=True, blank=True)

    def set_observable_props(self, x):
        self.observable_props = json.dumps(x)

    def get_observable_props(self):
        return json.loads(self.observable_props)

    def set_selected_observable_props(self, x):
        self.selected_observable_props = json.dumps(x)

    def get_selected_observable_props(self):
        return self.selected_observable_props

    def get_absolute_url(self):
        return '/sensors/%i' % self.id

    def get_thumbnail_url(self):
        return self.thumbnail_url

    def get_related_maps(self):
        sensor_maps = MapSensor.objects.filter(sensor=self.id)
        return sensor_maps


def pre_save_sensor(instance, sender, **kwargs):
    if kwargs.get('raw', False):
        instance.owner = instance.resourcebase_ptr.owner
        instance.uuid = instance.resourcebase_ptr.uuid

    if instance.abstract == '' or instance.abstract is None:
        instance.abstract = instance.description
    if instance.title == '' or instance.title is None:
        instance.title = instance.name
    if instance.thumbnail_url == '' or instance.thumbnail_url is None:
        instance.thumbnail_url = instance.selected_observable_props

    # Set a default user for accountstream to work correctly.
    if instance.owner is None:
        instance.owner = get_valid_user()

    if instance.uuid == '':
        instance.uuid = str(uuid.uuid1())

    #if instance.typename is None:
        # Set a sensible default for the typename
     #   instance.typename = 'OSH:%s' % instance.name


signals.pre_save.connect(pre_save_sensor, sender=Sensor)
signals.post_save.connect(resourcebase_post_save, sender=Sensor)

#This class/table just stores a registery of sensors and which maps they belong to
class MapSensor(models.Model):
    map = models.ForeignKey(Map)
    sensor = models.ForeignKey(Sensor)