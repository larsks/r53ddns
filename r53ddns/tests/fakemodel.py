from six import with_metaclass


class ConstraintError(Exception):
    pass


class TransactionIntegrityError (Exception):
    pass


def select(i):
    return i


def get(i):
    try:
        return next(i)
    except StopIteration:
        pass


def db_session(func):
    return func


class DBMeta(type):
    def __new__(cls, name, parents, dikt):
        dikt['_idseq'] = 0
        dikt['_oblist'] = []
        dikt['_obdict'] = {}

        return super(DBMeta, cls).__new__(cls, name, parents, dikt)

    def __iter__(self):
        return self.__classiter__()

    def __getitem__(self, id):
        return self._obdict[id]


class DBObject(with_metaclass(DBMeta, object)):
    _defaults = {}

    def __init__(self, **kwargs):
        self.check_create(**kwargs)

        self._dict = {}
        self._dict.update(self._defaults)
        for k, v in kwargs.items():
            self._dict[k] = v

        self.id = self.nextid()
        self._oblist.append(self)
        self._obdict[self.id] = self

    def check_create(self, *args, **kwargs):
        pass

    def check_delete(self):
        pass

    @classmethod
    def nextid(kls):
        kls._idseq += 1
        return kls._idseq

    def delete(self):
        self.check_delete()
        del self._obdict[self.id]
        self._oblist.remove(self)

    def flush(self):
        pass

    @classmethod
    def __classiter__(kls):
        return iter(kls._oblist)

    def __str__(self):
        return '%s[%d]' % (
            self.__class__.__name__,
            self.id,
        )

    def __repr__(self):
        return str(self)

    def __getattr__(self, k):
        if k.startswith('_'):
            raise AttributeError(k)
        else:
            try:
                return self._dict[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        if k.startswith('_'):
            super(DBObject, self).__setattr__(k, v)
        else:
            self._dict[k] = v

    def to_dict(self, *args, **kwargs):
        return self._dict

    @classmethod
    def reset(kls):
        kls._oblist = []
        kls._obdict = {}
        kls._idseq = 0

class Account(DBObject):
    _defaults = {
        'is_admin': False,
    }

    def check_create(self, *args, **kwargs):
        if kwargs['name'] in [a.name for a in self._oblist]:
            raise TransactionIntegrityError()


class Credentials(DBObject):
    def check_create(self, *args, **kwargs):
        if kwargs['name'] in [a.name for a in self._oblist
                              if a.owner is kwargs['owner']]:
            raise TransactionIntegrityError()

    def check_delete(self):
        for h in Host:
            if h.credentials is self:
                raise ConstraintError()


class Host(DBObject):
    def check_create(self, *args, **kwargs):
        if kwargs['name'] in [a.name for a in self._oblist
                              if a.credentials is kwargs['credentials']]:
            raise TransactionIntegrityError()

if __name__ == '__main__':
    user1 = Account(name='user1', password='secret')
    user2 = Account(name='user2', password='secret')
    user3 = Account(name='user3', password='secret')

    cred = Credentials(name='default',
                       secretkey='secretkey',
                       accesskey='accesskey',
                       owner=user3)
    Host(name='host.example.com',
         zone='example.com',
         credentials=cred)
