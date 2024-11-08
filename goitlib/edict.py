class Edict(dict):
    """
    A dictionary subclass that allows access to keys as attributes.
    All methods of a dictionary are available to an Edict object.
    """

    def __init__(self, **kwargs):
        dict.__setattr__(self, "__dict__", {})
        for k, v in kwargs.items():
            if isinstance(v, dict) and not isinstance(v, Edict):
                self.__setitem__(k, Edict(**v))
            else:
                self.__setitem__(k, v)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other

    def __ne__(self, other):
        return self.__dict__ != other

    def __hash__(self):
        return hash(self.__dict__)

    def __getattr__(self, key):
        return self.__dict__.get(key)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __delattr__(self, key):
        del self.__dict__[key]

    def __copy__(self):
        return Edict(**self.__dict__)

    def __deepcopy__(self, memo):
        return Edict(**self.__dict__)

    def copy(self):
        return self.__copy__()

    def deepcopy(self):
        return self.__deepcopy__()

    def update(self, other):
        self.__dict__.update(other)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, default)

    def pop(self, key, default=None):
        return self.__dict__.pop(key, default)

    def popitem(self):
        return self.__dict__.popitem()

    def clear(self):
        self.__dict__.clear()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def fromkeys(self, keys, value=None):
        return Edict(**dict.fromkeys(keys, value))

    def _to_dict(self, o):
        if isinstance(o, Edict):
            return {k: self._to_dict(v) for k, v in o.items()}
        else:
            return o

    def to_json(self):
        return json.dumps(self._to_dict(self.__dict__))

    def to_yaml(self):
        return yaml.dump(self._to_dict(self.__dict__))
