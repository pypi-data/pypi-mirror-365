from .conference import Conference

__version__ = "16.2.0"

_conf = Conference()
year = _conf.year()
location = _conf.location()
cfp = _conf.cfp()
dates = _conf.dates()
website = _conf.website()
theme = _conf.theme()
