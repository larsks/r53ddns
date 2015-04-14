from six import with_metaclass


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
        self._dict = {}
        self._dict.update(self._defaults)
        for k, v in kwargs.items():
            self._dict[k] = v

        self.id = self.nextid()
        self._oblist.append(self)
        self._obdict[self.id] = self

    @classmethod
    def nextid(kls):
        kls._idseq += 1
        return kls._idseq

    def delete(self):
        del self._obdict[self.id]

        print 'BEFORE:', self._oblist
        self._oblist = [o for o in self._oblist
                        if o.id != self.id]
        print 'AFTER:', self._oblist

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
        try:
            return self._dict[k]
        except KeyError:
            raise AttributeError(k)

    def to_dict(self, *args, **kwargs):
        return self._dict

class Account(DBObject):
    _defaults = {
        'is_admin': False,
    }

class Credentials(DBObject):
    pass

class Host(DBObject):
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
