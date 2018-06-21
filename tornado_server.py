import argparse
import logging

import itertools
from tornado import gen, ioloop, web, httpclient, httputil

import shared


class Parameters(object):
    def __init__(self, request_handler):
        # All parameters accepts one of: missing, tiny, low, normal, high, huge
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

    def initialize(self, backend_addresses):
        self.backend_addresses = backend_addresses

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
            base_url = '{}/simulate-backend'.format(next(self.backend_addresses))
            url = httputil.url_concat(base_url, params)
            yield async_client.fetch(url)

            # Simulate CPU work
            cpu_seconds = next(parameters.cpu_load_seq)
            shared.load_cpu(cpu_seconds)

        body = parameters.response_content
        self.write(body)


class ParallelIOHandler(web.RequestHandler):

    def initialize(self, backend_addresses):
        self.backend_addresses = backend_addresses

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
            base_url = '{}/simulate-backend'.format(next(self.backend_addresses))
            url = httputil.url_concat(base_url, params)
            yield async_client.fetch(url)

            # Simulate CPU work
            cpu_seconds = next(parameters.cpu_load_seq)
            shared.load_cpu(cpu_seconds)

        yield [chunk_of_work() for _ in range(parameters.io_number)]

        body = parameters.response_content
        self.write(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backend-ports', type=str, default='8080',
                        help='Comma separated ports where backend is listen on')
    parser.add_argument('-p', '--port', type=int, default=8082,
                        help='The port to listen on')
    parser.add_argument('-o', '--stats-output', type=str, default='tornado.log',
                        help='The file to write stats to')
    args = parser.parse_args()

    # Configure stats logger
    stats_log_file = logging.FileHandler(args.stats_output)
    stats_log_file.setFormatter(logging.Formatter(shared.STATS_LOG_FORMAT))
    shared.stats_logger.addHandler(stats_log_file)

    backend_addresses = itertools.cycle([
        'http://localhost:{}'.format(port)
        for port in args.backend_ports.split(',') if port
    ])
    backend_info = dict(backend_addresses=backend_addresses)
    app = web.Application([
        (r"/no-io", NoIOHandler),
        (r"/sequential-io", SequentialIOHandler, backend_info),
        (r"/parallel-io", ParallelIOHandler, backend_info),
    ])
    app.listen(args.port)
    io_loop = ioloop.IOLoop.current()
    ioloop.PeriodicCallback(shared.report_stats, 60000).start()
    io_loop.start()


if __name__ == '__main__':
    main()
