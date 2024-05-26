from prometheus_client import start_http_server, GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import requests
from prometheus_client.registry import Collector
import time
import os

WALLET = os.environ.get('WALLET')
if not WALLET:
    raise ValueError('WALLET environment variable is not set')
PORT = int(os.environ.get('PORT'))

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="124", "Brave";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

def get_wallet_points():
    url = f'https://app.ether.fi/api/portfolio/v3/{WALLET}'  # Replace with the URL of the website you want to scrape
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            points = {}
            for key, val in data['integrations'].items():
                key = key.replace('-', '_')
                if type(val) is dict and 'loyaltyPoints' in val:
                    points[f'etherfi_{key}_loyalty'] = val['loyaltyPoints']
                    points[f'etherfi_{key}_el'] = val['eigenlayerPoints']

            points['etherfi_loyalty_points'] = data['totalIntegrationLoyaltyPoints']
            points['etherfi_eigenlayer_points'] = data['totalIntegrationEigenLayerPoints']
            return points
        else:
            print("Failed to fetch website. Status code:", response.status_code)
    except Exception as e:
        print("Error occurred while scraping website:", e)
    return None


def get_total_points():
    url = 'https://app.ether.fi/api/points'
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Failed to fetch website. Status code:", response.status_code)
    except Exception as e:
        print("Error occurred while scraping website:", e)
    return None

class TotalPointsCollector(Collector):
    def collect(self):
        labels = [
            ('loyaltyPoints', 'etherfi_total_loyalty_points', 'Total Loyalty Points'),
            ('eigenLayerPoints', 'etherfi_total_eigenlayer_points', 'Total Eigenlayer Points'),
        ]
        data = get_total_points()
        for ele in labels:
            key, name, documentation = ele
            gauge_metric = GaugeMetricFamily(name, documentation, labels=[])
            gauge_metric.add_metric([], data[key])
            yield gauge_metric


class WalletPointsCollector(Collector):
    def collect(self):
        data = get_wallet_points()
        for key, value in data.items():
            gauge_metric = GaugeMetricFamily(key, f'{key} metric', labels=[])
            gauge_metric.add_metric([], value)
            yield gauge_metric


if __name__ == '__main__':
    start_http_server(PORT)

    REGISTRY.register(WalletPointsCollector())
    REGISTRY.register(TotalPointsCollector())

    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)

    print('Exporter started')

    while True:
        time.sleep(300)
