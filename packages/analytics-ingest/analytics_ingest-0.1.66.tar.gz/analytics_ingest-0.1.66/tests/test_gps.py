import unittest
from copy import deepcopy

from analytics_ingest.ingest_client import IcsAnalytics
from factories import configuration_factory, gps_factory, message_factory
from tests.test_settings import GRAPHQL_ENDPOINT


class TestAnalyticsGPSIntegeration(unittest.TestCase):
    def setUp(self):
        self.config_data = configuration_factory()
        self.client = IcsAnalytics(
            device_id=self.config_data['device_id'],
            vehicle_id=self.config_data['vehicle_id'],
            fleet_id=self.config_data['fleet_id'],
            org_id=self.config_data['organization_id'],
            batch_size=10,
            graphql_endpoint=GRAPHQL_ENDPOINT,
        )

    def test_add_gps_signal_with_factories(self):
        test_variables = gps_factory(num_entries=10)
        config_id = self.client.configuration_id
        self.assertIsInstance(config_id, int)
        self.client.add_gps(test_variables)

    def test_add_gps_with_valid_manual_data(self):
        valid_entry = gps_factory(num_entries=1)[0]
        gps_data = [valid_entry for _ in range(5)]
        try:
            self.client.add_gps(gps_data)
        except Exception as e:
            self.fail(f"Valid input raised unexpected error: {e}")

    def test_add_gps_missing_time(self):
        bad_entry = deepcopy(gps_factory(num_entries=1)[0])
        del bad_entry["time"]
        with self.assertRaises(Exception) as context:
            self.client.add_gps([bad_entry])
        self.assertIn("time", str(context.exception).lower())

    def test_add_gps_invalid_latitude_type(self):
        bad_entry = deepcopy(gps_factory(num_entries=1)[0])
        bad_entry["latitude"] = "not-a-float"
        with self.assertRaises(Exception) as context:
            self.client.add_gps([bad_entry])
        self.assertIn("latitude", str(context.exception).lower())

    def test_add_gps_empty_data_list(self):
        with self.assertRaises(ValueError) as context:
            self.client.add_gps([])
        self.assertIn("missing", str(context.exception).lower())

    def test_add_gps_missing_data_key(self):
        with self.assertRaises(ValueError) as context:
            self.client.add_gps(None)
        self.assertIn("missing", str(context.exception).lower())
