import pprint
from prometheus_client.core import GaugeMetricFamily, Counter, Gauge


class CustomCollector(object):
    namespace: str
    pp = pprint.PrettyPrinter(indent=4)

    def __init__(self, namespace: str, subsystem_prefix: str = '', subsystem_item_unit: str = ''):
        self.namespace: str = namespace
        self.subsystemPrefix: str = subsystem_prefix
        self.subsystemItemUnit: str = subsystem_item_unit
        self.metric: GaugeMetricFamily = None
        self.labels: [str] = []

        self.scrapesTotalMetric = Counter("total", f"Total number of scrapes for {self.subsystemPrefix} stats",
                                          subsystem=f"{self.subsystemPrefix}_scrapes",
                                          namespace=self.namespace)
        self.scrapeErrorsTotalMetric = Counter("total",
                                               f"Total number of scrape errors for {self.subsystemPrefix} stats",
                                               subsystem=f"{self.subsystemPrefix}_scrape_errors",
                                               namespace=self.namespace)
        self.lastScrapeErrorMetric = Gauge(f"last_{self.subsystemPrefix}_scrape_error",
                                           f"Status of last scrape for {self.subsystemPrefix} stats (1=error, 0=success)",
                                           subsystem="", namespace=self.namespace)
        self.lastScrapeTimestampMetric = Gauge(f"last_{self.subsystemPrefix}_scrape_timestamp",
                                               f"Number of seconds between 1970 and last scrape for {self.subsystemPrefix} stats",
                                               subsystem="", namespace=self.namespace)
        self.lastScrapeDurationSecondsMetric = Gauge(f"last_{self.subsystemPrefix}_scrape_duration_seconds",
                                                     f"Duration of last scrape for {self.subsystemPrefix} stats",
                                                     subsystem="", namespace=self.namespace)

    def build_name(self):
        full_name = ''
        if self.namespace:
            full_name += f"{self.namespace}_"
        if self.subsystemPrefix:
            full_name += f"{self.subsystemPrefix}_"
        if self.subsystemItemUnit:
            full_name += self.subsystemItemUnit

        return full_name

    '''
    This function resets the stats that are scraped from external apis
    '''

    def reset(self):
        metricName = self.build_name()
        metricDescription = f"{self.subsystemPrefix} measurement in {self.subsystemItemUnit}"

        self.metric = GaugeMetricFamily(metricName, metricDescription, labels=self.labels)

