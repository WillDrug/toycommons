import requests
from toycommons.model.service import Service
import threading
from requests.exceptions import ConnectionError
from time import sleep


class ToydiscoverAPI:
    """
    API to work with Discovery for the nginx; To be used by apps within toychest
    """
    def __init__(self, config: "Config", service: Service = None):
        """
        :param config: global config from toycommons.storage.config.
        """
        self.config = config
        self.__service = service
        self.__reporting = False

    @property
    def __url(self):
        """
        :return: str - full url to request services
        """
        return f'{self.config.discovery_url}/services'

    def do_report(self, retry=0):
        """
        POSTs request to ToyDiscover to report self.
        :return: None
        """
        try:
            requests.post(self.__url, headers={'Content-Type': 'application/json'}, data=self.__service.json())
        except ConnectionError as e:
            if retry < 3:  # todo: pretty this up if works
                sleep(10)
                return self.do_report(retry=retry+1)
            else:
                raise e

    def __report(self):
        """
        Infinite thread-based function.
        :return:
        """
        self.do_report()
        if self.__reporting:
            threading.Timer(self.config.discovery_ttl, self.__report).start()

    def set_params_and_start_reporting(self, hostname: str, name: str, description: str,
                                       image: str = None, tags: list = None):
        """
        Double-whammy function if you were too lazy to give Service object on init.
        """
        self.set_params(hostname, name, description, image=image, tags=tags)
        self.start_reporting()

    def set_params(self, hostname: str, name: str, description: str, image: str = None, tags: list = None):
        """
        Generates a new Service object
        :param hostname: App hostname
        :param name: App name
        :param description: App description
        :param image: URL to image (relative or full)
        :param tags: List of tags.
        :return: None
        """
        self.__service = Service(host=hostname, name=name, description=description, image=image, tags=tags)

    def start_reporting(self):
        """
        Start infinite reporting.
        :return:
        """
        self.__reporting = True
        self.__report()

    def stop_reporting(self):
        """
        Stop infinite reporting
        :return:
        """
        self.__reporting = False

    def get_services(self):
        """
        Get a current list of services running.
        :return:
        """
        rs = requests.get(self.__url, headers={'Content-Type': 'application/json'})
        return [Service(**q) for q in rs.json()]
