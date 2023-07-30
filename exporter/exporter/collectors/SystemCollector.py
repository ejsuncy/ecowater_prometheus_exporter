import time
import logging
import os

from prometheus_client.core import GaugeMetricFamily
from py_ecowater import EcowaterClient

from .CustomCollector import CustomCollector
from ..constants import EnvironmentVariableKeys as envkey


class SystemCollector(CustomCollector):

    def __init__(self, namespace: str):
        # the subsystem prefix is a name for the subsystem being scraped
        self.subsystemPrefix: str = "system"

        super().__init__(namespace, self.subsystemPrefix)

        username = os.getenv(envkey.ACCOUNT_USERNAME_KEY, None)
        password = os.getenv(envkey.ACCOUNT_PASSWORD_KEY, None)

        # make sure the username and password are set
        if not username or not password:
            logging.error(
                f"Username or password not set in environment variables {envkey.ACCOUNT_USERNAME_KEY} or {envkey.ACCOUNT_PASSWORD_KEY}")
            raise Exception("Username or password not set")

        # This is the client that calls external apis for the items to be scraped
        self.api_client: EcowaterClient = EcowaterClient(username, password)

        # the set of labels that describes each of the item attributes that you are scraping
        self.commonLabels: [str] = [
            "id",
            "serial_number",
            "nickname"
        ]

        # These are the metrics that are being scraped
        self.system_metric: GaugeMetricFamily = None
        self.alert_metric = None
        self.alarm_metric = None
        self.iron_level_tenths_ppm_metric = None
        self.hardness_unit_enum_metric = None
        self.hardness_grains_metric = None
        self.salt_level_tenths_value_metric = None
        self.salt_level_tenths_percent_metric = None
        self.salt_monitor_enum_metric = None
        self.volume_unit_enum_metric = None
        self.regen_enable_enum_metric = None
        self.regen_time_secs_metric = None
        self.time_format_enum_metric = None
        self.time_zone_enum_metric = None
        self.date_format_enum_metric = None
        self.water_shutoff_valve_req_metric = None
        self.total_water_available_gallons_metric = None
        self.current_water_flow_metric = None
        self.gallons_used_today_metric = None
        self.average_daily_use_gallons_metric = None
        self.regen_status_enum_metric = None
        self.out_of_salt_estimated_days_metric = None
        self.days_since_last_regen_metric = None
        self.system_type_value_metric = None
        self.system_type_type_metric = None
        self.water_shutoff_valve_metric = None
        self.water_shutoff_valve_installed_metric = None
        self.water_shutoff_valve_override_metric = None
        self.water_shutoff_valve_device_action_metric = None
        self.water_shutoff_valve_error_code_metric = None
        self.refresh_policy_metric = None

    def collect(self):
        time_start = time.time()
        logging.debug("Resetting per-call metrics")
        self.reset()

        logging.debug(f"Collecting {self.subsystemPrefix} stats")

        error_status = 0

        try:
            # this is where the api-scraping logic goes
            logging.debug(f"Collecting stats for {self.subsystemPrefix}")

            systems = self.api_client.get_systems()

            for system in systems.systems:
                system_state = self.api_client.get_system_state(system.serial_number)

                if not system_state:
                    logging.error(f"Could not get system state for {system.serial_number}")
                    raise Exception(f"Could not get system state for {system.serial_number}")

                common_label_values = [
                    system.id,
                    system.serial_number,
                    system.nickname
                ]

                self.system_metric.add_metric(
                    labels=common_label_values + [
                        system_state.base_software_version.value if system_state.base_software_version else "",
                        system.description.unit_owner if system.description else "",
                        str(system.description.rental_access) if system.description else "",
                        system.ac_role_name,
                        system.model_id,
                        system.model_name,
                        system.model_description,
                        str(system.dealer_access) if system.dealer_access else "False",
                        str(system.is_rental) if system.is_rental else "False",
                        str(system.is_restricted) if system.is_restricted else "False",
                        str(system.is_super_hero) if system.is_super_hero else "False",
                        str(system.is_filter_system) if system.is_filter_system else "False",
                        str(system.water_shut_off_valve_control) if system.water_shut_off_valve_control else "False",
                        str(system_state.power) if system_state.power else "False",
                        system_state.device_date.strftime("%m/%d/%Y, %H:%M:%S") if system_state.device_date else ""
                    ], value=1)

                self.alert_metric.add_metric(
                    labels=common_label_values, value=int(system.alerts_active) if system.alerts_active else 0)

                self.alarm_metric.add_metric(
                    labels=common_label_values, value=int(system.alarms_alerts) if system.alarms_alerts else 0)

                self.iron_level_tenths_ppm_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.iron_level_tenths_ppm.value if system_state.iron_level_tenths_ppm else 0)

                self.hardness_unit_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.hardness_unit_enum.value if system_state.hardness_unit_enum else 0)

                self.hardness_grains_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.hardness_grains.value if system_state.hardness_grains else 0)

                self.salt_level_tenths_value_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.salt_level_tenths.value if system_state.salt_level_tenths else 0)

                self.salt_level_tenths_percent_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.salt_level_tenths.percent if system_state.salt_level_tenths else 0)

                self.salt_monitor_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.salt_monitor_enum.value if system_state.salt_monitor_enum else 0)

                self.volume_unit_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.volume_unit_enum.value if system_state.volume_unit_enum else 0)

                self.regen_enable_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.regen_enable_enum.value if system_state.regen_enable_enum else 0)

                self.regen_time_secs_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.regen_time_secs.value if system_state.regen_time_secs else 0)

                self.time_format_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.time_format_enum.value if system_state.time_format_enum else 0)

                self.time_zone_enum_metric.add_metric(
                    labels=common_label_values + [
                        system_state.time_zone_enum.value if system_state.time_zone_enum else ""
                    ],
                    value=1)

                self.date_format_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.date_format_enum.value if system_state.date_format_enum else 0)

                self.water_shutoff_valve_req_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.water_shutoff_valve_req.value if system_state.water_shutoff_valve_req else 0)

                self.total_water_available_gallons_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.total_water_available_gallons.value if system_state.total_water_available_gallons else 0)

                self.current_water_flow_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.current_water_flow.value if system_state.current_water_flow else 0)

                self.gallons_used_today_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.gallons_used_today.value if system_state.gallons_used_today else 0)

                self.average_daily_use_gallons_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.average_daily_use_gallons.value if system_state.average_daily_use_gallons else 0)

                self.regen_status_enum_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.regen_status_enum.value if system_state.regen_status_enum else 0)

                self.out_of_salt_estimated_days_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.out_of_salt_estimated_days.value if system_state.out_of_salt_estimated_days else 0)

                self.days_since_last_regen_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.days_since_last_regen.value if system_state.days_since_last_regen else 0)

                self.system_type_value_metric.add_metric(
                    labels=common_label_values + [system_state.system_type.value if system_state.system_type else ""],
                    value=1)

                self.system_type_type_metric.add_metric(
                    labels=common_label_values + [system_state.system_type.type if system_state.system_type else ""],
                    value=1)

                self.water_shutoff_valve_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.water_shutoff_valve.value if system_state.water_shutoff_valve else 0)

                self.water_shutoff_valve_installed_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.water_shutoff_valve_installed.value if system_state.water_shutoff_valve_installed else 0)

                self.water_shutoff_valve_override_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.water_shutoff_valve_override.value if system_state.water_shutoff_valve_override else 0)

                self.water_shutoff_valve_device_action_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.water_shutoff_valve_device_action.value if system_state.water_shutoff_valve_device_action else 0)

                self.water_shutoff_valve_error_code_metric.add_metric(
                    labels=common_label_values,
                    value=system_state.water_shutoff_valve_error_code.value if system_state.water_shutoff_valve_error_code else 0)

                self.refresh_policy_metric.add_metric(
                    labels=common_label_values + [
                        system_state.refresh_policy.delay if system_state.refresh_policy else ""
                    ],
                    value=system_state.refresh_policy.time if system_state.refresh_policy else 0)

        except Exception as e:
            logging.error("Error while getting %s stats via client: %s", self.subsystemPrefix, e)
            error_status = 1
            self.scrapeErrorsTotalMetric.inc()

        self.scrapesTotalMetric.inc()
        self.lastScrapeErrorMetric.set(error_status)
        time_end = time.time()
        self.lastScrapeTimestampMetric.set(time_end)
        self.lastScrapeDurationSecondsMetric.set(time_end - time_start)

        return [
            self.system_metric,
            self.alert_metric,
            self.alarm_metric,
            self.iron_level_tenths_ppm_metric,
            self.hardness_unit_enum_metric,
            self.hardness_grains_metric,
            self.salt_level_tenths_value_metric,
            self.salt_level_tenths_percent_metric,
            self.salt_monitor_enum_metric,
            self.volume_unit_enum_metric,
            self.regen_enable_enum_metric,
            self.regen_time_secs_metric,
            self.time_format_enum_metric,
            self.time_zone_enum_metric,
            self.date_format_enum_metric,
            self.water_shutoff_valve_req_metric,
            self.total_water_available_gallons_metric,
            self.current_water_flow_metric,
            self.gallons_used_today_metric,
            self.average_daily_use_gallons_metric,
            self.regen_status_enum_metric,
            self.out_of_salt_estimated_days_metric,
            self.days_since_last_regen_metric,
            self.system_type_value_metric,
            self.system_type_type_metric,
            self.water_shutoff_valve_metric,
            self.water_shutoff_valve_installed_metric,
            self.water_shutoff_valve_override_metric,
            self.water_shutoff_valve_device_action_metric,
            self.water_shutoff_valve_error_code_metric,
            self.refresh_policy_metric
        ]

    '''
    This function resets the stats that are scraped from external apis
    '''

    def reset(self):
        self.system_metric = GaugeMetricFamily(
            self.build_name("attributes"),
            'System attributes',
            labels=self.commonLabels + [
                "base_software_version",
                "description_unit_owner",
                "description_rental_access",
                "ac_role_name",
                "model_id",
                "model_name",
                "model_description",
                "dealer_access",
                "is_rental",
                "is_restricted",
                "is_super_hero",
                "is_filter_system",
                "water_shutoff_valve_control",
                "power",
                "device_date"
            ])

        self.alert_metric = GaugeMetricFamily(
            self.build_name("alerts_enabled"),
            'System alerts enabled',
            labels=self.commonLabels)

        self.alarm_metric = GaugeMetricFamily(
            self.build_name("alarms_active"),
            'System alarms active',
            labels=self.commonLabels)

        self.iron_level_tenths_ppm_metric = GaugeMetricFamily(
            self.build_name("iron_level_tenths_ppm"),
            'System iron level tenths ppm',
            labels=self.commonLabels)

        self.hardness_unit_enum_metric = GaugeMetricFamily(
            self.build_name("hardness_unit_enum"),
            'System hardness unit enum - Salt Type - 0=NaCl, 1=KCl',
            labels=self.commonLabels)

        self.hardness_grains_metric = GaugeMetricFamily(
            self.build_name("hardness_grains"),
            'System hardness grains - inlet water hardness (1-140 gpg)',
            labels=self.commonLabels)

        self.salt_level_tenths_value_metric = GaugeMetricFamily(
            self.build_name("salt_level_tenths_value"),
            'System salt level tenths value',
            labels=self.commonLabels)

        self.salt_level_tenths_percent_metric = GaugeMetricFamily(
            self.build_name("salt_level_tenths_percent"),
            'System salt level tenths percent',
            labels=self.commonLabels)

        self.salt_monitor_enum_metric = GaugeMetricFamily(
            self.build_name("salt_monitor_enum"),
            'System salt monitor enum',
            labels=self.commonLabels)

        self.volume_unit_enum_metric = GaugeMetricFamily(
            self.build_name("volume_unit_enum"),
            'System volume unit enum - 0=Gallons, 1=Liters',
            labels=self.commonLabels)

        self.regen_enable_enum_metric = GaugeMetricFamily(
            self.build_name("regen_enable_enum"),
            'System regen enable enum - 0=Off, 1=On',
            labels=self.commonLabels)

        self.regen_time_secs_metric = GaugeMetricFamily(
            self.build_name("regen_time_secs"),
            'System regen time - secs after midnight. ie 7200 = 2am',
            labels=self.commonLabels)

        self.time_format_enum_metric = GaugeMetricFamily(
            self.build_name("time_format_enum"),
            'System time format enum - 0=12hr, 1=24hr',
            labels=self.commonLabels)

        self.time_zone_enum_metric = GaugeMetricFamily(
            self.build_name("time_zone_enum"),
            'System time zone enum',
            labels=self.commonLabels + ["time_zone"])

        self.date_format_enum_metric = GaugeMetricFamily(
            self.build_name("date_format_enum"),
            'System date format enum - 0=mm/dd/yyyy, 1=dd/mm/yyyy',
            labels=self.commonLabels)

        self.water_shutoff_valve_req_metric = GaugeMetricFamily(
            self.build_name("water_shutoff_valve_req"),
            'System water shutoff valve required',
            labels=self.commonLabels)

        self.total_water_available_gallons_metric = GaugeMetricFamily(
            self.build_name("total_water_available_gallons"),
            'System total water available gallons',
            labels=self.commonLabels)

        self.current_water_flow_metric = GaugeMetricFamily(
            self.build_name("current_water_flow"),
            'System current water flow',
            labels=self.commonLabels)

        self.gallons_used_today_metric = GaugeMetricFamily(
            self.build_name("gallons_used_today"),
            'System gallons used today',
            labels=self.commonLabels)

        self.average_daily_use_gallons_metric = GaugeMetricFamily(
            self.build_name("average_daily_use_gallons"),
            'System average daily use gallons',
            labels=self.commonLabels)

        self.regen_status_enum_metric = GaugeMetricFamily(
            self.build_name("regen_status_enum"),
            'System regen status enum - 0=Not Running, 1=Running',
            labels=self.commonLabels)

        self.out_of_salt_estimated_days_metric = GaugeMetricFamily(
            self.build_name("out_of_salt_estimated_days"),
            'System out of salt estimated days',
            labels=self.commonLabels)

        self.days_since_last_regen_metric = GaugeMetricFamily(
            self.build_name("days_since_last_regen"),
            'System days since last regen',
            labels=self.commonLabels)

        self.system_type_value_metric = GaugeMetricFamily(
            self.build_name("system_type_value"),
            'System system type value',
            labels=self.commonLabels + ["value"])

        self.system_type_type_metric = GaugeMetricFamily(
            self.build_name("system_type_type"),
            'System system type type',
            labels=self.commonLabels + ["type"])

        self.water_shutoff_valve_metric = GaugeMetricFamily(
            self.build_name("water_shutoff_valve"),
            'System water shutoff valve state',
            labels=self.commonLabels)

        self.water_shutoff_valve_installed_metric = GaugeMetricFamily(
            self.build_name("water_shutoff_valve_installed"),
            'System water shutoff valve installed',
            labels=self.commonLabels)

        self.water_shutoff_valve_override_metric = GaugeMetricFamily(
            self.build_name("water_shutoff_valve_override"),
            'System water shutoff valve override state',
            labels=self.commonLabels)

        self.water_shutoff_valve_device_action_metric = GaugeMetricFamily(
            self.build_name("water_shutoff_valve_device_action"),
            'System water shutoff valve device action state - whether the valve is currently opening or closing',
            labels=self.commonLabels)

        self.water_shutoff_valve_error_code_metric = GaugeMetricFamily(
            self.build_name("water_shutoff_valve_error_code"),
            'System water shutoff valve error code',
            labels=self.commonLabels)

        self.refresh_policy_metric = GaugeMetricFamily(
            self.build_name("refresh_policy_time"),
            'System refresh policy (ms). delay label describes low/med/high',
            labels=self.commonLabels + [
                "delay"
            ])
