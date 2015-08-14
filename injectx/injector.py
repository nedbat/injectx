"""Data injector."""

import random

from .catcher import start_catcher


THE_PORT = start_catcher()
THE_HOST = "nedx.com"       # TODO: get this from the caller.


def munge_default(name, val, payload):
    return val + payload

def munge_date(name, val, payload):
    return val

def munge_html(name, val, payload):
    return val

def seems_like_xml(name, val):
    """Crudely guess whether a value is XML."""
    sval = val.strip()
    if sval.startswith("<") and sval.endswith(">"):
        if sval.count("<") == sval.count(">"):
            return True

    return False

def munge_xml(name, val, payload):
    from xml.sax.saxutils import escape
    payload = escape(payload, {"'": "&apos;", '"': "&quot;"})
    sval = val.strip()
    assert sval.endswith(">")
    munged = sval[:-1].replace(">", ">"+payload) + ">"
    return munged


class Injector(object):
    def __init__(self, hints=None, rate=None):
        self.hints = hints or {}
        self.rate = rate

    def payload(self, name, val):
        return "<img src='http://%s:%s/?name=%s'>" % (THE_HOST, THE_PORT, name)

    def munge(self, name, val):
        if not isinstance(val, basestring):
            return val
        if self.rate is not None and random.random() > self.rate:
            return val

        valtype = None

        hint = self.hints.get(name, {})
        if hint.get("knownbad", False):
            return val
        valtype = hint.get("type", None)

        if valtype is None:
            if seems_like_xml(name, val):
                valtype = "xml"

        munger = globals()["munge_"+(valtype or "default")]
        payload = self.payload(name, val)
        munged = munger(name, val, payload)
        return munged
