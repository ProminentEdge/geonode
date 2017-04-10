from django import forms
from django.forms.extras import SelectDateWidget
#from django.forms.extras import SplitDateTimeWidget
from django.forms.widgets import SplitDateTimeWidget
from geonode.contrib.sensors.models import Sensor

DATE_FORMAT = '%m/%d/%Y'
TIME_FORMAT = '%I:%M %p'



class SensorForm(forms.ModelForm):

    class Meta:
        model = Sensor
        fields = ('name', 'offering_id', 'description', 'start_time', 'end_time',
                  'user_start_time', 'user_end_time', 'observable_props', 'selected_observable_props')
        widgets = {
            #'name': forms.Textarea(attrs={'cols': 80, 'rows': 1, 'disabled':True}),

        }


