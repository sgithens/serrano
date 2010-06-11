import imp
from copy import deepcopy

from django.conf import settings
from django.utils.importlib import import_module

class AlreadyRegisteredError(Exception):
    pass


class RegisterError(Exception):
    pass


class AbstractFormatter(object):
    """The AbstractFormatter defines the base behavior for formatting a set of
    arguments.
    """
    def __call__(*args, ftype=None):
        return getattr(self, ftype)(*args)


class FormatterLibrary(object):
    """The base class for defining a formatter library.

    This library dynamically determines the available formatter types via a
    user-defined setting `COLUMN_CONCEPT_FORMATTER_TYPES'. This provides the
    available to define any number of formatter types without needing to
    subclass or override any part of the library. An example as follows:

        COLUMN_CONCEPT_FORMATTER_TYPES = {
            'json': {
                'error': '[data format error]',
            },
            'html' : {
                'error': '<span class="data-format-error">[data format error]</span>',
                'null': '<span class="lg ht">(no data)</span>',
            },
            'csv': {
                'error': '[data format error]',
                'null': '',
            }
        }

    Every formatter registered must be a sublcass of the AbstractFormatter
    class. Each formatter can support any number of formatter types by simply
    defining a method of the same name, e.g:

        class MyFormatter(AbstractFormatter):
            def json(*args):
                return ' '.join(map(lambda x: str(x).upper(), args))

    The above formatter class supports the "json" formatter type but not
    either of the "html" or "csv" types. For formatters that need to support
    more than one type, but handles the input the same, the following
    convention should be used:

        class MyFormatter(AbstractFormatter):
            def json(*args):
                return ' '.join(map(lambda x: str(x).upper(), args))
            html = json

    The "html" formatter merely points to the "json" method.
    """

    FORMATTER_TYPES = getattr(settings, 'COLUMN_CONCEPT_FORMATTER_TYPES', {})

    def __init__(self):
        self._cache = deepcopy(self.FORMATTER_TYPES)
        for key in self._cache:
            self._cache[key]['formatters'] = {}

    def _parse_name(self, name):
        if name.endswith('Formatter'):
            name = name[:-9]
        toks = [name[0]]
        for x in name[1:]:
            if x.isupper():
                toks.append(' ')
            toks.append(x)
        return ''.join(toks)

    def register(self, klass):
        "Registers a Formatter subclass. The class name must be unique."
        if not issubclass(klass, AbstractFormatter):
            raise RegisterError, '%s must be a subclass of AbstractFormatter' % repr(klass)

        obj = klass()

        if hasattr(klass, 'name'):
            klass_name = klass.name
        else:
            klass_name = self._parse_name(klass.__name__)

        for ftype in self._ftypes:
            if hasattr(obj, ftype): # strange requirement?
                if self._cache[ftype]['formatters'].has_key(klass_name):
                    raise AlreadyRegisteredError, 'A formatter with the ' \
                        'name "%s" is already registered for the %s ' \
                        'formatter type' % (klass.name, ftype)
                self._cache[ftype][klass_name] = obj
        return klass

    def choices(self, ftype):
        "Returns a list of tuples that can be used as choices in a form."
        return [(n, n) for n in self._cache[ftype].keys()]

    def format_seq(self, seq, rules, idx, fhash):
        toks = []
        head = list(seq[:idx[0]])
        tail = list(seq[idx[1]:])

        data = seq[idx[0]:idx[1]]

        i = 0
        for fname, nargs in rules:
            # skip if the rule does not apply to anything
            if nargs == 0:
                continue

            obj = fhash['formatters'][fname]
            try:
                tok = obj(ftype, *data[i:i+nargs])
            except Exception:
                tok = fhash['error']

            if tok is None:
                tok = fhash.get('null', None)

            try:
                iter(tok)
                toks.extend(tok)
            except TypeError:
                toks.append(tok)

            i += nargs

        return tuple(head + toks + tail)

    def format(self, iterable, rules, ftype, idx=(1, None)):
        """Take an iterable and formats the data given the rules.

        Definitions:

            `iterable' - an iterable of iterables

            `rules' - a list of pairs defining the formatter name and the
            number of items to format, e.g. [('MyFormatter', 3),
            ('AnotherFormatter', 1)]

            `ftype' - a string specifying the formatter type

            `idx' - the slice of data to format per row. the data ignored
            will not be passed through the formatter, but will be retained and
            passed back with the the formatted data, e.g:

                class MyFormatter(AbstractFormatter):
                    def json(*args):
                        return ' '.join(map(lambda x: str(x).upper(), args))

                iterable    = [(3, 'foo', 746, 'bar', 392)]
                rules       = (2, 'afunc')
                ftype       = 'json'
                idx         = (1, 3)

                The result will be:

                    [('FOO', '848', 'BAR')]
        """
        fhash = self._cache[ftype]
        for seq in iter(iterable):
            yield self.format_row(seq, rules, idx, fhash)


LOADING = False

def autodiscover():
    global LOADING

    if LOADING:
        return
    LOADING = True

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('formatters', app_path)
        except ImportError:
            continue

        import_module('%s.formatters' % app)

    LOADING = False
