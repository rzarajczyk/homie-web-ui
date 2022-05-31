import requests
from typing import List

from plugins.plugin import Plugin, Link
from actions_server import Action, JsonPost, StaticResources, JsonGet


class ToyotaPlugin(Plugin):
    def __init__(self, config, plugin_root, url_root):
        Plugin.__init__(self, 'ToyotaPlugin')
        self.url = config['url']
        self.key = config['google-api-key']
        self.root_dir = plugin_root
        self.root_url = url_root

    def links(self) -> List[Link]:
        return [Link('Toyota', f'{self.root_url}/toyota.html')]

    def actions(self) -> List[Action]:
        return [
            JsonGet(f'{self.root_url}/data', self.data),
            JsonGet(f'{self.root_url}/apikey', self.api_key),
            JsonGet(f'{self.root_url}/trip', self.trip),
            StaticResources(f'{self.root_url}', '%s/web' % self.root_dir)
        ]

    def api_key(self, params):
        return {
            'apikey': self.key
        }

    def trip(self, params):
        trip_response = requests.get('%s/trip?id=%s' % (self.url, params['id'][0]))
        trip_response.raise_for_status()
        trip = trip_response.json()
        return trip

    def data(self, params):
        status_response = requests.get('%s/status' % self.url)
        status_response.raise_for_status()
        status = status_response.json()

        parking_response = requests.get('%s/parking' % self.url)
        parking_response.raise_for_status()
        parking = parking_response.json()

        trips_response = requests.get('%s/trips' % self.url)
        trips_response.raise_for_status()
        trips = trips_response.json()

        return {
            'status': {
                'vin': status['vin'],
                'plates': status['registration-number'],
                'fuel': status['fuel-left-percent'],
                'odo': status['odometer-km']
                },
            'parking': parking,
            'trips': trips
        }
