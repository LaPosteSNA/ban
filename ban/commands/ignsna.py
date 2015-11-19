import json
import pathlib
import glob
import os

from ban.commands import command, report
from ban.core.models import (HouseNumber, Locality, Municipality, Position,
                             Street)

from .helpers import batch, iter_file, session


__namespace__ = 'import'


@command
def ignsna(path):
    """Import from IGN/Laposte BDUNI"""

    municipality_zipcode_file = glob.glob(os.path.join(path, 'hsp7*.ai'))
    street_file = glob.glob(os.path.join(path, 'hsv7*.ai'))
    number_file = glob.glob(os.path.join(path, 'hsw4*.ai'))

    print(municipality_zipcode_file)
    print(street_file)
    print(number_file)

    if municipality_zipcode_file is not None:
        process_municipality_file(municipality_zipcode_file)

    if street_file is not None:
        process_streetFile(street_file)

    if number_file is not None:
        process_numberFile(number_file)


    #max_value = sum(1 for line in iter_file(path))
    #rows = iter_file(path, formatter=json.loads)
    #batch(process_row, rows, chunksize=100, max_value=max_value)


def process_municipality_file(municipality_zip_code_file):
    max_value = sum(1 for line in iter_file(municipality_zip_code_file))
    f = open(municipality_zip_code_file)
    lines = f.readlines()
    for x in range(2, max_value):
        line = lines[x]
        if line[51] == 'M':
            pass
    #rows = iter_file(path, formatter=json.loads)
    #batch(process_row, rows, chunksize=100, max_value=max_value)
    pass


def process_streetFile(streetfile):
    pass


def process_numberFile(numberfile):
    pass


@session
def process_row(metadata):
    name = metadata.get('name')
    id = metadata.get('id')
    insee = metadata.get('citycode')
    fantoir = ''.join(id.split('_')[:2])[:9]

    kind = metadata['type']
    klass = Street if kind == 'street' else Locality
    instance = klass.select().where(klass.fantoir == fantoir).first()
    if instance:
        return report('Existing', metadata)

    try:
        municipality = Municipality.get(Municipality.insee == insee)
    except Municipality.DoesNotExist:
        return report('Error', 'Municipality does not exist: {}'.format(insee))

    data = dict(
        name=name,
        fantoir=fantoir,
        municipality=municipality.id,
        version=1,
    )
    validator = klass.validator(**data)

    if not validator.errors:
        item = validator.save()
        report(kind, item)
        housenumbers = metadata.get('housenumbers')
        if housenumbers:
            for id, metadata in housenumbers.items():
                add_housenumber(item, id, metadata)
    else:
        report('Error', validator.errors)


def add_housenumber(parent, id, metadata):
    number, *ordinal = id.split(' ')
    ordinal = ordinal[0] if ordinal else ''
    center = [metadata['lon'], metadata['lat']]
    data = dict(number=number, ordinal=ordinal, version=1)
    data[parent.__class__.__name__.lower()] = parent.id
    validator = HouseNumber.validator(**data)

    if not validator.errors:
        housenumber = validator.save()
        validator = Position.validator(center=center, version=1,
                                       housenumber=housenumber.id)
        if not validator.errors:
            validator.save()
    else:
        report('Error', validator.errors)
