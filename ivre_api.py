import requests


class IvreAPI:
    def __init__(self, url):
        self.ivre_url = url

    def get_hosts(self, q):
        url = f"http://{self.ivre_url}/cgi/scans/ipsports?q={q}"

        try:
            req = requests.get(url, headers={'Referer': f'http://{self.ivre_url}/'})
            return req.json()

        except requests.exceptions.RequestException as e:
            err = "Alert create error: {}".format(e)
            return err
