class BaseColumnHeader(object):
    def __init__(self, request, id, column):
        self.id = id
        self.request = request
        self.column = column

    def __unicode__(self):
        return self.column.label


class Column(object):
    creation_counter = 0

    def __init__(self, label, refname=None, **attrs):
        self.label = label
        self.refname = refname
        self.attrs = attrs

        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1


class LabelColumn(Column):
    pass
