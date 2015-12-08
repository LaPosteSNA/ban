import glob
import os
from progressbar import ProgressBar

from ban.commands import command, report
from ban.core.models import (HouseNumber, Locality, Municipality, Position,
                             Street)
from .helpers import iter_file, session

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
    import ipdb; ipdb.set_trace()
    if municipality_zipcode_file is not None:
        process_municipality_file(municipality_zipcode_file[0])


    if street_file is not None:
        process_streetFile(street_file[0])

    if number_file is not None:
        process_numberFile(number_file[0])


    #max_value = sum(1 for line in iter_file(path))
    #rows = iter_file(path, formatter=json.loads)
    #batch(process_row, rows, chunksize=100, max_value=max_value)

@session
def process_municipality_file(municipality_zip_code_file):
    max_value = get_max_line(municipality_zip_code_file)
    lines = get_lines(municipality_zip_code_file)
    pbar = ProgressBar()
    for x in pbar(range(0, max_value)):
        line = lines[x]
        if line[50] == 'M':
            insee = line[6:11]
            name = line[11:49]
            zip_code = line[89:94]
            old_insee = line[126:131]

            try:
                municipality = Municipality.get(Municipality.insee == insee)

            except Municipality.DoesNotExist:
                data = dict(insee=insee, name=name, siren='99999', version='1', zipcode= zip_code)
                validator = Municipality.validator(**data)
                if not validator.errors:
                    validator.save(validator)
                else:
                    return report('Error', validator.errors)


@session
def process_streetFile(street_file):
    max_value = get_max_line(street_file)
    lines = get_lines(street_file)
    pbar = ProgressBar()
    for x in pbar(range(0, max_value)):
        line = lines[x]
        if line[0] == 'V':
            insee = line[7:12]
            name = line[60:92]
            zip_code = line[109:114]


            try:
                municipality = Municipality.get(Municipality.insee == insee)

            except Municipality.DoesNotExist:
                return report('Error', 'Municipality does not exist: {}'.format(insee))

            try:
                street = Street.get(Street.name == name and Street.municipality == municipality.id)
            except Street.DoesNotExist:
                data = dict(
                    name=name,
                    municipality=municipality.id,
                    version=1,
                    fantoir=Street.tmp_fantoir(),
                    zipcode=zip_code,
                )
                validator = Street.validator(**data)
                if not validator.errors:
                    item = validator.save()
                else:
                    report('Error', validator.errors)




def get_lines(file):
    f = open(file)
    lines = f.readlines()
    return lines


def get_max_line(file):
    max_value = sum(1 for line in iter_file(file))
    return max_value


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