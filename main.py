import time
import logging
from typing import Dict

from exporter import TemplateCollector
from exporter import EnvironmentParser,FileParser

from prometheus_client import start_http_server, REGISTRY


class ExporterApplication():
    def __init__(self):
        self.exporter_namespace: str = None
        self.exporter_port: str = None
        self.exporter_bind_host: str = None
        self.app_configs: Dict = None

    def register_collectors(self):
        logging.debug("Initializing and registering TemplateCollector")
        collector = TemplateCollector(self.exporter_namespace)
        REGISTRY.register(collector)

    def start_server(self):
        if app.app_configs:
            logging.info("App namespace from config file: %s", app.app_configs['namespace'])
        logging.info("Starting server on %s:%s", self.exporter_bind_host, self.exporter_port)
        start_http_server(port=int(self.exporter_port), addr=self.exporter_bind_host)

        # Keep the main thread active so the daemon threads can handle requests
        while True:
            time.sleep(1)


if __name__ == '__main__':
    app = ExporterApplication()
    EnvironmentParser.parse_logging_config(app)
    EnvironmentParser.parse_server_config(app)
    FileParser.parse_app_configs(app)
    app.register_collectors()
    app.start_server()
