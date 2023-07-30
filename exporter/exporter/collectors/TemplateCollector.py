import time
import logging
from .CustomCollector import CustomCollector
from prometheus_client.core import GaugeMetricFamily


class TemplateCollector(CustomCollector):

    def __init__(self, namespace: str):
        # the subsystem prefix is a name for the subsystem being scraped
        self.subsystemPrefix: str = "template_subsystem"
        # subsystemItemUnit is the name of the subsystem item unit that is being scraped
        self.subsystemItemUnit: str = "template_item_unit"

        super().__init__(namespace, self.subsystemPrefix, self.subsystemItemUnit)

        # This is the client that calls external apis for the items to be scraped
        self.api_client: TemplateClient

        # This is the metric that is being scraped
        self.metric: GaugeMetricFamily = None

        # the set of labels that describes each of the item attributes that you are scraping
        self.labels: [str] = ["template_attr1", "template_attr2"]

    def collect(self):
        time_start = time.time()
        logging.debug("Resetting per-call metrics")
        self.reset()

        logging.debug(f"Collecting {self.subsystemPrefix} stats")

        error_status = 0

        try:
            # this is where the api-scraping logic goes
            logging.debug(f"Collecting stats for {self.subsystemPrefix}")

            # items = self.api_client.get_items()
            # for item in items:
            #     label_values = []
            #     for label in self.labels:
            #         label_value = item.get(label)
            #         label_values.append(label_value)
            #     self.metric.add_metric(
            #         labels=label_values, value=item.metric_value)

        except Exception as e:
            logging.error("Error while getting %s stats via client: %s", self.subsystemPrefix, e)
            error_status = 1
            self.scrapeErrorsTotalMetric.inc()

        self.scrapesTotalMetric.inc()
        self.lastScrapeErrorMetric.set(error_status)
        time_end = time.time()
        self.lastScrapeTimestampMetric.set(time_end)
        self.lastScrapeDurationSecondsMetric.set(time_end - time_start)

        return [self.metric]
