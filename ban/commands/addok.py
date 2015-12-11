from pathlib import Path

from ban.commands import command, report

from ban.core import models, versioning
from ban.core.encoder import dumps


@command
def exp_resources(path, **kwargs):
    """Export database as resources to addok.

    path    path of file where to write resources
    """
    resources = [models.ZipCode, models.Municipality, models.Locality,
                 models.Street, models.HouseNumber]
    goe_resources = [models.Locality, models.Street, models.HouseNumber]
    with Path(path).open(mode='w', encoding='utf-8') as f:

        for resource in (models.Street.select()):
            street_name = resource.name
            importance = 1/4
            if not street_name.find('Boulevard') == -1 or not street_name.find('Place') == -1 or not street_name.find('Espl') == -1:
                importance = 4/4
            elif not street_name.find('Av') == -1:
                importance = 3/4
            elif not street_name.find('Rue') == -1:
                importance = 2/4

            response = ('"id": "{}_{}", "type": "{}", "name": "{}", "insee": "{}", "insee": "{}", "lon": 0, "lat": 0, "city": "{}", "importance": "{:.4f}" '.format(resource.municipality.insee, resource.fantoir, resource.resource, resource.name, resource.municipality.insee, resource.municipality.insee, resource.municipality.name, importance)) # +'"cea":"{} ", '.format(resource.get('cea'))
            hns = '"housenumbers": {'
            for hn in models.HouseNumber.select().where(models.HouseNumber.street == resource).as_resource():

                f.write(dumps(hn) + '\n')
                # Memory consumption when exporting all France housenumbers?
            # report(resouce.__name__, resouce)
                report(hn.get('cia'), hn)



@command
def exp_diff(path, **kwargs):
    """Export diff to addok.

    path    path of file where to write resources
    """
    with Path(path).open(mode='w', encoding='utf-8') as f:
        resource = versioning.Diff
        for data in resource.select().where(resource.id == '1').as_resource():
            resource_id = data['resource_id']
            diff = data['diff']
            resource_type = data['resource']
            increment = data['increment']
            new = data['new']
            attrib = getattr(models, resource_type[0:1].upper()+resource_type[1:])
            for allA in attrib.select().where(attrib.id == new['id']).as_resource():
                allA



            f.write(dumps(data) + '\n')
            # Memory consumption when exporting all France housenumbers?
            report(resource.__name__, data)