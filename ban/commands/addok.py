from pathlib import Path

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
            for data in models.Street.select().join(models.Municipality).where(models.Street.municipality_id == models.Municipality.id).as_resource_list(): # .where(models.HouseNumber.street == models.Street.identifiers ).as_resource_list():
                f.write(dumps(data) + '\n')
                # Memory consumption when exporting all France housenumbers?
                report(resource.__name__, data)
