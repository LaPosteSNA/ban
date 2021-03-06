import peewee

from .connections import default


class SelectQuery(peewee.SelectQuery):

    def _get_result_wrapper(self):
        return getattr(self, '_result_wrapper', None) \
                                            or super()._get_result_wrapper()

    def __len__(self):
        return self.count()


class Model(peewee.Model):

    class Meta:
        database = default
        manager = SelectQuery

    # TODO find a way not to override the peewee.Model select classmethod.
    @classmethod
    def select(cls, *selection):
        query = cls._meta.manager(cls, *selection)
        if cls._meta.order_by:
            query = query.order_by(*cls._meta.order_by)
        return query

    @classmethod
    def where(cls, *expressions):
        """Shortcut for select().where()"""
        return cls.select().where(*expressions)

    @classmethod
    def first(cls, *expressions):
        """Shortcut for select().where().first()"""
        qs = cls.select()
        if expressions:
            qs = qs.where(*expressions)
        return qs.first()
