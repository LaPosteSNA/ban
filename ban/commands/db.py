import sys

from ban.auth import models as amodels
from ban.commands import command
from ban.core import models as cmodels
from ban.core.versioning import Version

from .helpers import prompt

models = [Version, amodels.User, amodels.Client, amodels.Grant,
          amodels.Session, amodels.Token, cmodels.Municipality,
          cmodels.Street, cmodels.Locality, cmodels.HouseNumber,
          cmodels.Position, cmodels.ZipCode]


@command
def syncdb(fail_silently=False):
    """Create database tables.

    fail_silently   Do not raise error if table already exists.
    """
    for model in models:
        model.create_table(fail_silently=fail_silently)


@command
def createuser(username=None, email=None, is_staff=True):
    """Create a user.

    is_staff    set user staff
    """
    if not username:
        username = prompt('Username')
    if not email:
        email = prompt('Email')
    password = prompt('Password', confirmation=True)
    validator = amodels.User.validator(username=username, email=email)
    if not validator.errors:
        user = validator.save()
        user.set_password(password)
        if is_staff:
            user.is_staff = True
            user.save()
    else:
        for field, error in validator.errors.items():
            sys.stderr.write('{}: {}\n'.format(field, error))
