from tornado import gen, ioloop, web, httpclient, httputil

import shared


class Parameters(object):
    def __init__(self, request_handler):
        # All parameters accepts one of: missing, tiny, small, normal, big, huge
        io_duration = request_handler.get_argument('io_duration_type', 'tiny')
        io_number = request_handler.get_argument('io_number_type', 'tiny')
        io_traffic = request_handler.get_argument('io_traffic_type', 'tiny')
        response_size = request_handler.get_argument('response_type', 'tiny')
        cpu_load = request_handler.get_argument('cpu_type', 'tiny')

        try:
            self.io_duration_seq = shared.DURATIONS[io_duration]
            self.io_number = shared.IO_NUMBER[io_number]
            self.io_traffic = io_traffic
            self.response_content = shared.RESPONSE_FILES[response_size]
            self.cpu_load_seq = shared.CPU_LOADS[cpu_load]
        except KeyError:
            raise web.HTTPError(400)


class NoIOHandler(web.RequestHandler):

    @gen.coroutine
    def get(self):
        parameters = Parameters(self)
        cpu_seconds = next(parameters.cpu_load_seq)
        shared.load_cpu(cpu_seconds)
        body = parameters.response_content
        self.write(body)


class SequentialIOHandler(web.RequestHandler):

    def initialize(self, backend_address):
        self.backend_address = backend_address

    @gen.coroutine
    def get(self):
        parameters = Parameters(self)
        async_client = httpclient.AsyncHTTPClient()

        for _ in range(parameters.io_number):

            # Make a request to dummy backend
            io_duration = next(parameters.io_duration_seq)
            params = {
                'duration': str(io_duration),
                'response_type': parameters.io_traffic
            }
            url = httputil.url_concat(
                'http://{}/simulate-backend'.format(self.backend_address), params
            )
            yield async_client.fetch(url)

            # Simulate CPU work
            cpu_seconds = next(parameters.cpu_load_seq)
            shared.load_cpu(cpu_seconds)

        body = parameters.response_content
        self.write(body)


class ParallelIOHandler(web.RequestHandler):

    def initialize(self, backend_address):
        self.backend_address = backend_address

    @gen.coroutine
    def get(self):
        parameters = Parameters(self)
        async_client = httpclient.AsyncHTTPClient()

        @gen.coroutine
        def chunk_of_work():
            # Make a request to dummy backend
            io_duration = next(parameters.io_duration_seq)
            params = {
                'duration': str(io_duration),
                'response_type': parameters.io_traffic
            }
            url = httputil.url_concat(
                'http://{}/simulate-backend'.format(self.backend_address), params
            )
            yield async_client.fetch(url)

            # Simulate CPU work
            cpu_seconds = next(parameters.cpu_load_seq)
            shared.load_cpu(cpu_seconds)

        yield [chunk_of_work() for _ in range(parameters.io_number)]

        body = parameters.response_content
        self.write(body)


def main():
    backend_info = dict(backend_address='localhost:8080')
    app = web.Application([
        (r"/no-io", NoIOHandler),
        (r"/sequential-io", SequentialIOHandler, backend_info),
        (r"/parallel-io", ParallelIOHandler, backend_info),
    ])
    app.listen(8082)
    io_loop = ioloop.IOLoop.current()
    ioloop.PeriodicCallback(shared.report_stats, 60000).start()
    io_loop.start()


if __name__ == '__main__':
    main()
