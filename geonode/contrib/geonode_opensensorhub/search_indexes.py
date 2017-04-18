from haystack import indexes
from geonode.contrib.geonode_opensensorhub.models import Sensor

class SensorIndex(indexes.SearchIndex, indexes.Indexable):
    id = indexes.IntegerField(model_attr='id')
    detail_url = indexes.CharField(model_attr="get_absolute_url")
    owner__username = indexes.CharField(model_attr="owner", faceted=True, null=True)
    offering_id = indexes.CharField(model_attr="offering_id")

    def get_model(self):
        return Sensor

    def prepare_type(self, obj):
        return "sensor"