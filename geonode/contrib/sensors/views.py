import urllib2
import xml.etree.ElementTree as ET
import json
import owslib

from datetime import datetime
import dateutil.parser

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.forms import formset_factory
from django.conf import settings
from django.template import RequestContext
from django.utils.translation import ugettext as _

from geonode.utils import resolve_object
from geonode.contrib.sensors.forms import SensorForm
from geonode.contrib.sensors.models import Sensor, SensorServer
from geonode.services.models import Service
from geonode.security.views import _perms_info_json

from guardian.shortcuts import get_perms


_PERMISSION_MSG_DELETE = _("You are not permitted to delete this layer")
_PERMISSION_MSG_GENERIC = _('You do not have permissions for this layer.')
_PERMISSION_MSG_MODIFY = _("You are not permitted to modify this layer")
_PERMISSION_MSG_METADATA = _(
    "You are not permitted to modify this layer's metadata")
_PERMISSION_MSG_VIEW = _("You are not permitted to view this layer")

req_context = {}
serverUrl = ""

class doublequote_dict(dict):
        def __str__(self):
            return json.dumps(self)

def _resolve_sensor(request, typename, permission='base.view_resourcebase',
                   msg=_PERMISSION_MSG_GENERIC, **kwargs):
    """
    Resolve the layer by the provided typename (which may include service name) and check the optional permission.
    """
    service_typename = typename.split(":", 1)

    if Service.objects.filter(name=service_typename[0]).exists():
        service = Service.objects.filter(name=service_typename[0])
        return resolve_object(request,
                              Sensor,
                              {'service': service[0],
                               'typename': service_typename[1] if service[0].method != "C" else typename},
                              permission=permission,
                              permission_msg=msg,
                              **kwargs)
    else:
        return resolve_object(request,
                              Sensor,
                              {'typename': typename,
                               'service': None},
                              permission=permission,
                              permission_msg=msg,
                              **kwargs)


@login_required
def sensors_add(request, template='sensors_add.html'):
    if request.method == 'GET':
        global serverUrl
        serverUrl=request.GET.get('serverUrl')
        if(serverUrl):
            reqUrl = serverUrl
            if(serverUrl[len(serverUrl)-1] != '/'):
                reqUrl += "/sos?service=SOS&version=2.0&request=GetCapabilities"
            else:
                reqUrl += "sos?service=SOS&version=2.0&request=GetCapabilities"
            try: httpResponse = urllib2.urlopen(reqUrl);
            except urllib2.URLError as e:
                return HttpResponse(e.reason)

            root = ET.fromstring(httpResponse.read())
            global req_context
            req_context = {'serverUrl': serverUrl, 'offerings':[]}

            # namespace dictionary to help make iterating over elements less verbose below
            ns = {'swes': 'http://www.opengis.net/swes/2.0',
                  'sos' : 'http://www.opengis.net/sos/2.0',
                  'gml' : 'http://www.opengis.net/gml/3.2'}

            offering_list = root.findall('*//sos:ObservationOffering', ns)

            for offering in offering_list:
                name = offering.find('swes:name', ns)
                id = offering.find('swes:identifier', ns)
                desc = offering.find('swes:description', ns)

                # get all the info we need for the offering (name, desc, time range, etc.)
                offeringInfo = {}
                for begin_time in offering.iterfind('*//gml:beginPosition', ns):
                    if begin_time.text is None:
                        offeringInfo['start_time'] = 'now'
                        offeringInfo['user_start_time'] = datetime.now()
                    else:
                        offeringInfo['start_time'] = begin_time.text.replace('T', ' ')
                        offeringInfo['user_start_time'] = dateutil.parser.parse(begin_time.text)
                for end_time in offering.iterfind('*//gml:endPosition', ns):
                    if end_time.text is None:
                        offeringInfo['end_time'] = 'now'
                        offeringInfo['user_end_time'] = datetime.now()
                    else:
                        offeringInfo['end_time'] = end_time.text.replace('T', ' ')
                        offeringInfo['user_end_time'] = dateutil.parser.parse(end_time.text)
                offeringInfo['name'] = name.text
                offeringInfo['offering_id'] = id.text
                offeringInfo['description'] = desc.text
                offeringInfo['observable_props'] = []
                offeringInfo['selected_observable_props'] = ""

                for observable_property in offering.findall('swes:observableProperty', ns):
                    offeringInfo['observable_props'].append(observable_property.text)# = "disabled"

                req_context['offerings'].append(offeringInfo)

            sensor_formset = formset_factory(SensorForm, extra=0)
            formset = sensor_formset(initial=req_context['offerings'])
            req_context['formset'] = formset
            return render_to_response(template, RequestContext(request, req_context))
        else:
            return render(request, template)
    elif request.method == 'POST':
        active_offerings = []
        debug = ''
        global req_context
        global serverUrl
        for offering in req_context['offerings']:
             if request.POST[offering['offering_id']] == "On":
                 active_offerings.append(offering['offering_id'])

        sensor_formset = formset_factory(SensorForm, extra=0)
        formset = sensor_formset(request.POST)
        if (len(active_offerings) != 0):
            for sensor_form in formset:
                if sensor_form.is_valid():
                    for active_offering in active_offerings:
                        sensor_model = sensor_form.save(commit=False)
                        if sensor_model.offering_id == active_offering:
                            debug += sensor_form.cleaned_data['selected_observable_props']
                            debug += sensor_form.cleaned_data['observable_props']
                            try:
                                server = SensorServer.objects.get(url=serverUrl)
                            except SensorServer.DoesNotExist:
                                server = SensorServer(url=serverUrl)
                            server.save()
                            sensor_model.server = server
                            sensor_model.save()
                else:
                    for field in sensor_form:
                        for error in field.errors:
                            debug += str(count) + ' : ' + field.label + ' : ' + error + '<br>'
                    count += 1
                    return render_to_response(template, RequestContext(request, req_context))
        else:
            return render_to_response(template, RequestContext(request, req_context))
        return HttpResponseRedirect(reverse('sensors_browse'))


def sensor_detail(request, sensor_id, template='sensor_detail.html'):
    if request.method == 'GET':
        global req_context
        try:
            sensor = Sensor.objects.get(id=sensor_id)
        except Sensor.DoesNotExist:
            return HttpResponse("Sensor does not exist");
            pass

        # TODO
        # Update count for popularity ranking,
        # but do not includes admins or resource owners
        # Example:
        # if request.user != sensor.owner and not request.user.is_superuser:
        #    Sensor.objects.filter(
        #        id=sensor.id).update(popular_count=F('popular_count') + 1)

        obs_props_string = sensor.observable_props
        sensor.observable_props = sensor.observable_props.split(',')

        sel_obs_props_string = sensor.selected_observable_props
        sensor.selected_observable_props = sensor.selected_observable_props.split(',')

        req_context = {
            "resource": sensor,
            "obs_props_string": obs_props_string,
            "sel_obs_props_string": sel_obs_props_string,
            'perms_list': get_perms(request.user, sensor.get_self_resource()),
            #"permissions_json": _perms_info_json(sensor),
            #"metadata": metadata,
            "is_layer": False,
        }

        # TODO
        # update context data depending on user perms
        # Example:
        # if request.user.has_perm('view_resourcebase', sensor.get_self_resource()):
        #   req["links"] = links_view

        return render_to_response(template, RequestContext(request, req_context))

    if request.method == 'POST':
        global req_context

        try:
            sensor = Sensor.objects.get(id=req_context['resource'].id)
        except Sensor.DoesNotExist:
            return HttpResponse("Sensor does not exist");
            pass

        sensor.selected_observable_props = request.POST['selected-observable-props']
        sensor.save()

        obs_props_string = sensor.observable_props
        sensor.observable_props = sensor.observable_props.split(',')

        sel_obs_props_string = sensor.selected_observable_props
        sensor.selected_observable_props = sensor.selected_observable_props.split(',')
        req_context = {
            "resource": sensor,
            "obs_props_string": obs_props_string,
            "sel_obs_props_string": sel_obs_props_string,
            'perms_list': get_perms(request.user, sensor.get_self_resource()),
            #"permissions_json": _perms_info_json(sensor),
            #"metadata": metadata,
            "is_layer": False,
        }

        return render_to_response(template, RequestContext(request, req_context))