import requests

from plugins.plugin import Plugin, Link
from server import Action, JsonPost, StaticResources, JsonGet


class ToyotaPlugin(Plugin):
    def __init__(self, config, plugin_root):
        Plugin.__init__(self, 'ToyotaPlugin')
        self.url = config['url']
        self.key = config['google-api-key']
        self.root = plugin_root

    def links(self) -> list[Link]:
        return [Link('Toyota', '/toyota/toyota.html')]

    def actions(self) -> list[Action]:
        return [
            JsonGet('/toyota/data', self.data),
            JsonGet('/toyota/apikey', self.api_key),
            JsonGet('/toyota/trip', self.trip),
            StaticResources('/toyota', '%s/web' % self.root)
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

    # def scan(self, params, payload):
    #     self.logger.info('Requesting scanner')
    #     response = requests.post('%s/scan' % self.url)
    #     response.raise_for_status()
    #     return response.json()
    #
    # def scanner_ready(self, params):
    #     self.logger.info('Checking scanner readiness')
    #     response = requests.get('%s/print/info' % self.url)
    #     return {'ready': response.status_code == 200}
