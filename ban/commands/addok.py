from pathlib import Path
import platform
from peewee import fn

from ban.commands import command, report

from ban.core import models, versioning
from ban.core.encoder import dumps


def make_municipality(action, municipality):
    importance = 1
    orig_center = {'lon': 0, 'lat': 0, 'zipcode': None}
    if municipality.zipcodes:
        orig_center['zipcode'] = municipality.zipcodes[0]
    response = (
    '["id": "{}", "type": "{}", "name": "{}", "zipcode": "{}", "lon": "{}", "lat": "{}", "city": "{}", "importance": "{:.4f}"]'.format(
        municipality.insee, municipality.resource, municipality.name, orig_center['zipcode'], orig_center['lon'], orig_center['lat'],
        municipality.name, importance))
    return cleanning_response(response)


@command
def exp_resources(path, **kwargs):
    """Export database as resources to addok.

    path    path of file where to write resources
    """
    resources = [models.ZipCode, models.Municipality, models.Locality,
                 models.Street, models.HouseNumber]
    goe_resources = [models.Locality, models.Street, models.HouseNumber]
    _encoding = 'utf-8'
    if platform.system() == 'Windows':
        _encoding = 'Latin-1'
    with Path(path).open(mode='w', encoding=_encoding) as f:
        action = ''

        for resource in (models.Municipality.select()):
            response = make_municipality(action, resource)
            f.write(response + '\n')

        for resource in (models.Street.select() and models.Locality.select()):
            response = make_hns(action, resource)

            f.write(response + '\n')
                # Memory consumption when exporting all France housenumbers?
            # report(resouce.__name__, resouce)
            report(resource.name, resource)


def make_hns(action, resource):
    importance = get_importance(resource.name)
    hns = ""
    orig_center = {'lon': 0, 'lat': 0, 'zipcode': None}
    municipality = models.Municipality.get(models.Municipality.name == resource.municipality.name)
    if municipality.zipcodes:
        orig_center['zipcode'] = municipality.zipcodes[0]
    for hn in models.HouseNumber.select().join(models.Position).where(
                            models.HouseNumber == models.Position.housenumber and (models.HouseNumber.street == resource or models.HouseNumber.locality == resource)):
        if hn.number == 0:
            orig_center['lon'] = hn.center['coordinates'][0]
            orig_center['lat'] = hn.center['coordinates'][1]

        else:
            part = '"{}": ["lat":"{}", "lon":"{}", "id": "{}", "cea": "{}", "zipcode": "{}"], '.format((hn.number+' '+hn.ordinal).strip(),
                                                                                 hn.center['coordinates'][0],
                                                                                 hn.center['coordinates'][1], hn.cia,
                                                                                 hn.cea, hn.zipcode)
            hns = hns + part

    hns = '"housenumbers": {' + hns[:-2] + '}'
    response = (
    '["id": "{}_{}", "type": "{}", "name": "{}", "insee": "{}", "zipcode": "{}", "lon": "{}", "lat": "{}", "city": "{}","context": "{},{}", "importance": "{:.4f}", {}]'.format(
        resource.municipality.insee, resource.fantoir, resource.resource, resource.name, resource.municipality.insee, orig_center['zipcode'], orig_center['lon'], orig_center['lat'],
        resource.municipality.name, resource.name, resource.municipality.name, importance, hns))
    if action is 'update':
        response = '["_action": "update", ' + response[1:]
    return cleanning_response(response)


def cleanning_response(response):
    response = response.replace(']', '}')
    response = response.replace('[', '{')
    return response


def get_importance(street_name):
    importance = 1 / 4
    if not street_name.find('Boulevard') == -1 or not street_name.find('Place') == -1 or not street_name.find(
            'Espl') == -1:
        importance = 4 / 4
    elif not street_name.find('Av') == -1:
        importance = 3 / 4
    elif not street_name.find('Rue') == -1:
        importance = 2 / 4
    return importance


@command
def exp_diff(path, **kwargs):
    """Export diff to addok.

    path    path of file where to write resources
    """
    _encoding = 'utf-8'
    if platform.system() == 'Windows':
        _encoding = 'Latin-1'
    with Path(path).open(mode='w', encoding=_encoding) as f:
        version = versioning.Diff
        for data in version.select().where(version.id == '1').as_resource():
            resource_id = data['resource_id']
            diff = data['diff']
            resource_type = data['resource']
            increment = data['increment']
            new = data['new']

            action = 'update'
            if new == 'None':
                action = 'delete'

            attrib = getattr(models, resource_type[0:1].upper()+resource_type[1:])
            allA = attrib.select().where(attrib.id == resource_id)

            response = make_hns(action, allA)

            f.write(response + '\n')
                    # Memory consumption when exporting all France housenumbers?
                # report(resouce.__name__, resouce)
            report(allA.name, allA)



            f.write(dumps(data) + '\n')
            # Memory consumption when exporting all France housenumbers?
            report(version.__name__, data)