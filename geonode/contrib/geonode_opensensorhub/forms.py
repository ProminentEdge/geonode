from django import forms
from django.forms.extras import SelectDateWidget
#from django.forms.extras import SplitDateTimeWidget
from django.forms.widgets import SplitDateTimeWidget
from geonode.contrib.geonode_opensensorhub.models import Sensor

DATE_FORMAT = '%m/%d/%Y'
TIME_FORMAT = '%I:%M %p'


class SensorForm(forms.ModelForm):

    #these 'temp' fields are used for intermediary/rendering purposes and will not be serialized
    temp_enabled = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = Sensor
        fields = ('name', 'procedure_id', 'offering_id', 'description', 'start_time', 'end_time',
                  'user_start_time', 'user_end_time', 'observable_props', 'selected_observable_props', 'config_name')
        widgets = {
            'config_name': forms.TextInput(attrs={'cols': 64, 'rows': 1, 'placeholder': '-required-'}),
            'user_start_time': forms.widgets.DateTimeInput(format=("%Y-%m-%d %H:%M:%S.%f")),
            'user_end_time': forms.widgets.DateTimeInput(format=("%Y-%m-%d %H:%M:%S.%f")),
        }





