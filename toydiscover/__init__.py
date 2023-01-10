import requests
from toycommons.model.service import Service
import threading


class ToydiscoverAPI:
    def __init__(self, config):
        self.config = config
        self.__serivce = None
        self.__reporting = False

    @property
    def __url(self):
        return f'{self.config.discovery_url}/services'

    def do_report(self):
        requests.post(self.__url, headers={'Content-Type': 'application/json'}, data=self.__serivce.json())

    def __report(self):
        self.do_report()
        if self.__reporting:
            threading.Timer(self.config.discovery_ttl, self.__report).start()

    def start_reporting(self, hostname, name, description, image=None, tags=None):
        self.__serivce = Service(host=hostname, name=name, description=description, image=image, tags=tags)
        self.__reporting = True
        self.__report()

    def stop_reporting(self):
        self.__reporting = False

    def get_services(self):
        rs = requests.get(self.__url, headers={'Content-Type': 'application/json'})
        return [Service(**q) for q in rs.json()]
