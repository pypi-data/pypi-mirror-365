from datetime import date
import re


def classendar_base(cls):
    """Class decorator for date-versioned classes"""
    original_init = cls.__init__

    # Store original get method if it exists
    original_get = getattr(cls, 'get', None)

    # __init__ make a copy into _init_kwargs as instance variable value
    def __init__(self, *args, **kwargs):
        self._init_kwargs = kwargs.copy()
        if original_init:
            original_init(self, *args, **kwargs)

    cls.__init__ = __init__

    if original_get:  # modify the original get method so that it will invoke the dated object
        async def get(self, *args, **kwargs):
            version_date = kwargs.get('version_date') or date.today()
            versioned_cls = _get_versioned_subclass(cls, version_date)
            if versioned_cls is not self.__class__:
                return await versioned_cls(**self._init_kwargs).get(*args, **kwargs)
            return await original_get(self, *args, **kwargs)

        cls.get = get

    # Add versioning methods to the class
    cls._get_versioned_subclass = classmethod(_get_versioned_subclass)
    cls._collect_subclasses = classmethod(_collect_subclasses)

    return cls


def _get_versioned_subclass(cls, target_date):
    if not hasattr(cls, '_subclass_cache'):
        cls._subclass_cache = {}

    if cls not in cls._subclass_cache:  # the subclass map is not set up
        cls._subclass_cache[cls] = _collect_subclasses(cls)

    for subclass, subclass_date in sorted(
        cls._subclass_cache[cls].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        if target_date >= subclass_date:
            return subclass  # get the subclass that is the closest lower than requested date
    return cls


def _collect_subclasses(cls):
    subclasses = {}

    def _recursive_collect(base_class):
        for subclass in base_class.__subclasses__():
            match = re.search(r'_(\d{4})(\d{2})(\d{2})$', subclass.__name__)
            if match:
                year, month, day = map(int, match.groups())
                subclasses[subclass] = date(year, month, day)
            _recursive_collect(subclass)

    _recursive_collect(cls)
    return subclasses
