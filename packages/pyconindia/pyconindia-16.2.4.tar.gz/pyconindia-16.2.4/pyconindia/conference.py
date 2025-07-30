"""
Conference Actions
"""

import yaml
import os
from datetime import datetime, date
from pathlib import Path


class Conference:
    def __init__(self):
        self._data = None
        self._load_data()

    def _load_data(self):
        if self._data is None:
            data_file = Path(__file__).parent / 'data' / 'conferences.yaml' 
            with open(data_file, 'r', encoding='utf-8') as f:
                self._data = yaml.safe_load(f)

    def year(self):
        return datetime.today().year

    def city(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('city', 'TBA')

    def state(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('state', 'TBA')

    def venue(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('venue', 'TBA')

    def location(self, year=None):
        year = year or self.year()
        city = self.city(year)
        state = self.state(year)
        venue = self.venue(year)
        
        if state and state != 'TBA':
            return f"{venue}, {city}, {state}, India"
        else:
            return f"{venue}, {city}"

    def month(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('month', 'TBA')

    def dates(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        month = conf_data.get('month', 'TBA')
        date_info = conf_data.get('date', {})
        
        start_date = date_info.get('start')
        end_date = date_info.get('end')
        
        if start_date and end_date:
            if start_date == end_date:
                return f"{month} {start_date}, {year}"
            else:
                return f"{month} {start_date}-{end_date}, {year}"
        elif start_date:
            return f"{month} {start_date}, {year}"
        else:
            return f"{month} {year} (TBA)"

    def status(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        current_year = self.year()
        
        if not conf_data:
            if year > current_year:
                return "not_planned"
            else:
                return "prehistoric"
        
        month_name = conf_data.get('month', '').lower()
        date_info = conf_data.get('date', {})
        start_date = date_info.get('start')
        end_date = date_info.get('end')
        
        if not month_name or not start_date:
            return "upcoming"
        
        # Map month names to numbers
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        month_num = month_map.get(month_name)
        if not month_num:
            return "upcoming"
        
        try:
            today = date.today()
            
            # Handle cross-month conferences (like Aug 30 - Sep 1)
            if end_date and start_date > end_date:
                # Conference spans two months
                start_conference = date(year, month_num, start_date)
                # End date is in the next month
                end_month = month_num + 1 if month_num < 12 else 1
                end_year = year if month_num < 12 else year + 1
                end_conference = date(end_year, end_month, end_date)
            else:
                start_conference = date(year, month_num, start_date)
                end_conference = date(year, month_num, end_date or start_date)
            
            if today < start_conference:
                return "upcoming"
            elif start_conference <= today <= end_conference:
                return "happening"
            else:
                return "over"
                
        except (ValueError, TypeError):
            return "upcoming"

    def cfp(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        cfp_url = conf_data.get('cfp_url')
        
        if cfp_url:
            return f"Submit your proposal: {cfp_url}"
        return "CFP is closed"

    def website(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('website', f'https://in.pycon.org/{year}/')

    def tickets(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('tickets', 'TBA')

    def schedule(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        schedule_url = conf_data.get('schedule_url')
        
        if schedule_url:
            return f"View schedule: {schedule_url}"
        return "Schedule not prepared yet"

    def get_all_years(self):
        return sorted(self._data.keys())

    def get_conference_info(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        current_year = self.year()
        
        if not conf_data:
            if year > current_year:
                # Future year not planned yet
                return {
                    'year': year,
                    'city': 'TBA',
                    'state': 'TBA',
                    'venue': 'TBA',
                    'location': 'Not Planned Yet! Want to organise? Reach out to mailing list "https://mail.python.org/mailman3/lists/inpycon.python.org/"',
                    'month': 'TBA',
                    'dates': 'TBA',
                    'status': 'not_planned',
                    'cfp': 'Not Planned Yet! Want to organise? Reach out to mailing list "https://mail.python.org/mailman3/lists/inpycon.python.org/"',
                    'tickets': 'Not Planned Yet! Want to organise? Reach out to mailing list "https://mail.python.org/mailman3/lists/inpycon.python.org/"',
                    'schedule': 'Not Planned Yet! Want to organise? Reach out to mailing list "https://mail.python.org/mailman3/lists/inpycon.python.org/"',
                    'website': f'https://in.pycon.org/{year}/'
                }
            else:
                # Past year before PyCon India existed
                return {
                    'year': year,
                    'city': 'TBA',
                    'state': 'TBA',
                    'venue': 'TBA',
                    'location': 'Pre-historic times when PyCon India did not exist',
                    'month': 'TBA',
                    'dates': 'Pre-historic times when PyCon India did not exist',
                    'status': 'prehistoric',
                    'cfp': 'Pre-historic times when PyCon India did not exist',
                    'tickets': 'Pre-historic times when PyCon India did not exist',
                    'schedule': 'Pre-historic times when PyCon India did not exist',
                    'website': f'https://in.pycon.org/{year}/'
                }
        
        return {
            'year': year,
            'city': self.city(year),
            'state': self.state(year),
            'venue': self.venue(year),
            'location': self.location(year),
            'month': self.month(year),
            'dates': self.dates(year),
            'status': self.status(year),
            'cfp': self.cfp(year),
            'tickets': self.tickets(year),
            'schedule': self.schedule(year),
            'website': self.website(year)
        }
