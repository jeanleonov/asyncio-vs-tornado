import os
from os.path import abspath, dirname, join

from locust import HttpLocust, TaskSet, task
import yaml

DEFAULT_CONFIG_FILE = join(dirname(abspath(__file__)),
                           'test-scenarios',
                           'highops_lowdelay_tinycpu.yml')
CONFIG_FILE_PATH = os.environ.get('SCENARIO', DEFAULT_CONFIG_FILE)

try:
    # Read test configuration from the file
    with open(CONFIG_FILE_PATH) as config_file:
        TEST_CONFIG = yaml.load(config_file)

    # Define user behavior according to config
    class ClientBehavior(TaskSet):

        @task(TEST_CONFIG['no-io']['weight'])
        def no_io(self):
            self.client.get(
                "/no-io", params=TEST_CONFIG['no-io']['params'])

        @task(TEST_CONFIG['sequential-io']['weight'])
        def sequential_io(self):
            self.client.get(
                "/sequential-io", params=TEST_CONFIG['sequential-io']['params'])

        @task(TEST_CONFIG['parallel-io']['weight'])
        def parallel_io(self):
            self.client.get(
                "/parallel-io", params=TEST_CONFIG['parallel-io']['params'])

except (KeyError, ValueError, OSError) as err:
    raise ValueError(
        'Invalid configuration file at {}. '
        'The YAML configuration file should contain three nodes: '
        '"no-io", "sequential-io", "parallel-io". Each of nodes should have '
        '"weight" (integer) and "params" (dict).'.format(CONFIG_FILE_PATH)
    ) from err


class WebsiteUser(HttpLocust):
    task_set = ClientBehavior
    min_wait = 800
    max_wait = 1200
