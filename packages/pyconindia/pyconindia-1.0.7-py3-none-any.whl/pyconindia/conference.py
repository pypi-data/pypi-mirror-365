"""
Conference Actions
"""

from datetime import datetime


class Conference:
    def __init__(self):
        return

    def year(self):
        """
        Get Current Year
        """
        today = datetime.today()
        return today.year

    def location(self, year=None):
        if not year:
            year = self.year()
        return self.__get_current_location(year)

    def cfp(self, year=None):
        if not year:
            year = self.year()
        return self.__get_cfp_status(year)

    def __get_current_location(self, year):
        # TODO: get location data from year wise yaml file
        location = "Anywhere on Earth"
        return location

    def __get_cfp_status(self, year):
        # TODO: get cfp state based on year
        return f"Find more about Call For Proposals at: https://in.pycon.org/cfp/{year}/proposals/"
