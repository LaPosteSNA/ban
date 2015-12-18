from pathlib import Path
import os
import platform

from ban.commands import command, report
from ban.core import models, versioning


def make_municipality(action, municipality):
    importance = 1
    orig_center = {'lon': 0, 'lat': 0, 'zipcode': None}
    if municipality.zipcodes:
        orig_center['zipcode'] = municipality.zipcodes[0]
    response = (
        '["id": "{}", "type": "{}", "name": "{}", "zipcode": "{}", "lon": "{}", "lat": "{}", "city": "{}", "importance": "{:.4f}"]'.format(
                municipality.insee, municipality.resource, municipality.name, orig_center['zipcode'],
                orig_center['lon'], orig_center['lat'],
                municipality.name, importance))
    if action is 'update':
        response = '["_action": "update", ' + response[1:]
    return cleanning_response(response)


@command
def exp_resources(path, **kwargs):
    """Export database as resources to addok.

    path    path of file where to write resources
    """
    resources = [models.ZipCode, models.Municipality, models.Locality,
                 models.Street, models.HouseNumber]
    goe_resources = [models.Locality, models.Street, models.HouseNumber]
    with Path(path).open(mode='w', encoding='utf-8') as f:
        action = ''

        for resource in (models.Municipality.select()):
            write_responce(action, make_municipality(action, resource), f)

        for resource in (models.Street.select()):
            write_responce(action, make_hns(action, resource), f)

        for resource in (models.Locality.select()):
            write_responce(action, make_hns(action, resource), f)


def make_hns(action, resource):
    importance = 1
    hns = ""
    orig_center = {'lon': 0, 'lat': 0, 'zipcode': None}
    if resource.resource == 'housenumber':
        query = models.HouseNumber.select().join(models.Position).where(
                                models.HouseNumber == models.Position.housenumber and (
                                models.HouseNumber.street == resource.street or models.HouseNumber.locality == resource.locality) and models.HouseNumber.id == resource )
        for hn in query:
            if hn.street.name:
                importance = get_importance(hn.street.name)
                resource = models.Street.get(models.Street.id == hn.street)
            elif hn.locality.name:
                importance = get_importance(hn.locality.name)
                resource = models.Locality.get(models.Locality.id == hn.locality)

            hns = make_a_housenumber(hn, hns, orig_center)

    else:
        importance = get_importance(resource.name)
        for hn in models.HouseNumber.select().join(models.Position).where(
                                models.HouseNumber == models.Position.housenumber and (
                                models.HouseNumber.street == resource or models.HouseNumber.locality == resource)):
            hns = make_a_housenumber(hn, hns, orig_center)

    hns = '"housenumbers":{' + hns[:-2] + '}'
    response = (
        '["id": "{}_{}", "type": "{}", "name": "{}", "insee": "{}", "zipcode": "{}", "lon": "{}", "lat": "{}", "city": "{}","context": "{},{}", "importance": {:.4f} , {}]'.format(
                resource.municipality.insee, resource.fantoir, resource.resource, resource.name,
                resource.municipality.insee, orig_center['zipcode'], orig_center['lon'], orig_center['lat'],
                resource.municipality.name, resource.name, resource.municipality.name, importance, hns))
    if action is 'update':
        response = '["_action": "update", ' + response[1:]
    return cleanning_response(response)


def make_a_housenumber(hn, hns, orig_center):
    if hn.number == 0:
        orig_center['lon'] = hn.center['coordinates'][0]
        orig_center['lat'] = hn.center['coordinates'][1]

    else:
        part = '"{}": ["lat": {}, "lon": {}, "id": "{}", "cea": "{}", "zipcode": "{}"], '.format(
                (hn.number + ' ' + hn.ordinal).strip(),
                hn.center['coordinates'][0],
                hn.center['coordinates'][1], hn.cia,
                12345678, hn.zipcode)  # hn.cea#, hn.zipcode)
        hns = hns + part
    return hns


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

    path    file path to write resources
    """
    _encoding = 'utf-8'
    if platform.system() == 'Windows':
        _encoding = 'Latin-1'
    version = versioning.Diff
    for data in version.select().as_resource():
        resource_id = data['resource_id']
        diff = data['diff']
        resource_type = data['resource']
        increment = data['increment']
        new = data['new']

        with Path(os.path.join(path, 'diff_' + str(increment) + '.json')).open(mode='w', encoding=_encoding) as f:

            action = 'update'
            if new == 'None':
                action = 'delete'

            if resource_type == 'housenumber':
                attrib = getattr(models, 'HouseNumber')
            else:
                attrib = getattr(models, resource_type[0:1].upper() + resource_type[1:])

            if attrib is models.Municipality:
                municipality = attrib.get(models.Municipality.id == resource_id)
                response = make_municipality(action, municipality)
                f.write(response + '\n')

                for resource in (models.Street.select().where(models.Street.municipality == municipality)):
                    write_responce(action, make_hns(action, resource), f)

                for resource in (models.Locality.select().where(models.Locality.municipality == municipality)):
                    write_responce(action, make_hns(action, resource), f)

            if attrib is models.Locality or attrib is models.Street:
                write_responce(action, make_hns(action, attrib.get()), f)

            if attrib is models.HouseNumber:
                hn = attrib.get(models.HouseNumber.id == resource_id)
                write_responce(action, make_hns(action, hn), f)
            report(version.__name__, data)


def write_responce(action, response, in_file):
    in_file.write(response + '\n')
    # Memory consumption when exporting all France housenumbers?
    # report(resouce.__name__, resouce)
