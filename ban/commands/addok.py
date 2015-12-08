from pathlib import Path

from peewee import RawQuery, fn

from ban.commands import command, report
from ban.core import models
from ban.core.encoder import dumps


@command
def export_all(path, **kwargs):
    """Export database as resources in json stream format to addok.

    path    path of file where to write resources
    """
    resources = [models.HouseNumber]
    with Path(path).open(mode='w', encoding='utf-8') as f:
        for resource in resources:
            resco = {}
            for data in models.Street.select().as_resource():
                resco = data
                resco['type'] = models.Street.__name__
                resco['housenumbers'] = []
                print(data.get('id'))
                rec = {}
                for dat in models.HouseNumber.select().where(models.HouseNumber.street == data.get('id')).as_resource():
                    for da in dat:
                        rec = {dat['number'], da}
                    resco['housenumbers'].append(rec)
                write_to_file(resco, f, resource)


def write_to_file(data, f, resource):
    f.write(dumps(data) + '\n')
    # Memory consumption when exporting all France housenumbers?
    report(resource.__name__, data)
