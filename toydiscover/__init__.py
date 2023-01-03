import requests
from toycommons.model.service import Service
import threading


class ToydiscoverAPI:
    def __init__(self, config):
        self.config = config
        self.__serivce = None
        self.__reporting = False

    def __report(self):
        requests.post(f'{self.config.discovery_url}/services', headers={'Content-Type': 'application/json'},
                      data=self.__serivce.json())
        if self.__reporting:
            threading.Timer(self.config.discovery_ttl, self.__report).start()

    def start_reporting(self, hostname, name, description):
        self.__serivce = Service(host=hostname, name=name, description=description)
        self.__reporting = True
        self.__report()

    def stop_reporting(self):
        self.__reporting = False

    def get_services(self):
        rs = requests.get(f'{self.config.discovery_url}/services', headers={'Content-Type': 'application/json'})
        return [Service(**q) for q in rs.json()]
