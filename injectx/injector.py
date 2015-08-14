"""Data injector."""

import random

from .catcher import start_catcher


THE_PORT = start_catcher()
THE_HOST = "nedx.com"       # TODO: get this from the caller.


def munge_default(name, val, payload):
    return val + payload

def seems_like_xml(name, val):
    """Crudely guess whether a value is XML."""
    sval = val.strip()
    if sval.startswith("<") and sval.endswith("<"):
        if sval.count("<") == sval.count(">"):
            return True

    return False

def munge_xml(name, val, payload):
    from xml.sax.saxutils import escape
    payload = escape(payload, {"'": "&apos;", '"': "&quot;"})
    munged = val.replace(">", ">"+payload)
    return munged


class Injector(object):
    def __init__(self, skip=None, rate=None):
        self.skip = skip or set()
        self.rate = rate

    def payload(self, name, val):
        return "<img src='http://%s:%s/?name=%s'>" % (THE_HOST, THE_PORT, name)

    def munge(self, name, val):
        valtype = "default"

        if name in self.skip:
            return val
        if not isinstance(val, basestring):
            return val
        if self.rate is not None and random.random() > self.rate:
            return val

        payload = self.payload(name, val)

        if seems_like_xml(name, val):
            return munge_xml(name, val, payload)
        else:
            return munge_default(name, val, payload)
