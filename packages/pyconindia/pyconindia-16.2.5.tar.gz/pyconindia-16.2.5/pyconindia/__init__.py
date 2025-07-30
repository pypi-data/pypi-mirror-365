from .conference import Conference

__version__ = "16.2.5"

_conf = Conference()
year = _conf.year()
city = _conf.city()
state = _conf.state()
venue = _conf.venue()
location = _conf.location()
month = _conf.month()
dates = _conf.dates()
status = _conf.status()
cfp = _conf.cfp()
tickets = _conf.tickets()
schedule = _conf.schedule()
website = _conf.website()
