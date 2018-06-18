from locust import HttpLocust, TaskSet, task


class ClientBehavior(TaskSet):

    @task(10)
    def no_io(self):
        self.client.get("/no-io", params={
            'response_type': 'small',
            'cpu_type': 'small',
        })

    @task(10)
    def sequential_io(self):
        self.client.get("/sequential-io", params={
            'io_duration_type': 'small',
            'io_number_type': 'normal',
            'io_traffic_type': 'small',
            'response_type': 'small',
            'cpu_type': 'small',
        })

    @task(10)
    def parallel_io(self):
        self.client.get("/parallel-io", params={
            'io_duration_type': 'small',
            'io_number_type': 'normal',
            'io_traffic_type': 'small',
            'response_type': 'small',
            'cpu_type': 'small',
        })


class WebsiteUser(HttpLocust):
    task_set = ClientBehavior
    min_wait = 800
    max_wait = 1200
