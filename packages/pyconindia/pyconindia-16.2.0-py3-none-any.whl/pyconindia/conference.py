"""
Conference Actions
"""

import yaml
import os
from datetime import datetime
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

    def location(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('location', 'TBA')

    def dates(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('dates', 'TBA')

    def cfp(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        cfp_url = conf_data.get('cfp_url')
        
        if cfp_url:
            return f"Submit your proposal: {cfp_url}"
        return f"Find more about Call For Proposals at: https://in.pycon.org/cfp/{year}/proposals/"

    def website(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('website', f'https://in.pycon.org/{year}/')

    def theme(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        return conf_data.get('theme', 'TBA')

    def get_all_years(self):
        return sorted(self._data.keys())

    def get_conference_info(self, year=None):
        year = year or self.year()
        conf_data = self._data.get(year, {})
        
        if not conf_data:
            return {
                'year': year,
                'location': 'TBA',
                'dates': 'TBA',
                'cfp': self.cfp(year),
                'website': f'https://in.pycon.org/{year}/',
                'theme': 'TBA'
            }
        
        return {
            'year': year,
            'location': conf_data.get('location', 'TBA'),
            'dates': conf_data.get('dates', 'TBA'),
            'cfp': self.cfp(year),
            'website': conf_data.get('website', f'https://in.pycon.org/{year}/'),
            'theme': conf_data.get('theme', 'TBA')
        }
