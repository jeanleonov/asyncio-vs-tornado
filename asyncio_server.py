import argparse
import asyncio
import logging

import aiohttp
import itertools
from aiohttp import web

import shared


class Parameters(object):
    def __init__(self, request):
        # All parameters accepts one of: missing, tiny, low, normal, high, huge
        io_duration = request.query.get('io_duration_type', 'tiny')
        io_number = request.query.get('io_number_type', 'tiny')
        io_traffic = request.query.get('io_traffic_type', 'tiny')
        response_size = request.query.get('response_type', 'tiny')
        cpu_load = request.query.get('cpu_type', 'tiny')

        try:
            self.io_duration_seq = shared.DURATIONS[io_duration]
            self.io_number = shared.IO_NUMBER[io_number]
            self.io_traffic = io_traffic
            self.response_content = shared.RESPONSE_FILES[response_size]
            self.cpu_load_seq = shared.CPU_LOADS[cpu_load]
        except KeyError:
            raise web.HTTPBadRequest()


class Server(object):
    def __init__(self, backend_addresses):
        self.backend_addresses = backend_addresses

    @staticmethod
    async def no_io(request):
        parameters = Parameters(request)
        cpu_seconds = next(parameters.cpu_load_seq)
        shared.load_cpu(cpu_seconds)
        body = parameters.response_content
        return web.Response(body=body)

    async def sequential_io(self, request):
        parameters = Parameters(request)
        async with aiohttp.ClientSession() as session:
            for _ in range(parameters.io_number):

                # Make a request to dummy backend
                io_duration = next(parameters.io_duration_seq)
                url = f'{next(self.backend_addresses)}/simulate-backend'
                params = {
                    'duration': str(io_duration),
                    'response_type': parameters.io_traffic
                }
                await session.get(url, params=params)

                # Simulate CPU work
                cpu_seconds = next(parameters.cpu_load_seq)
                shared.load_cpu(cpu_seconds)

        body = parameters.response_content
        return web.Response(body=body)

    async def parallel_io(self, request):
        parameters = Parameters(request)
        async with aiohttp.ClientSession() as session:

            async def chunk_of_work():

                # Make a request to dummy backend
                io_duration = next(parameters.io_duration_seq)
                url = f'{next(self.backend_addresses)}/simulate-backend'
                params = {
                    'duration': str(io_duration),
                    'response_type': parameters.io_traffic
                }
                await session.get(url, params=params)

                # Simulate CPU work
                cpu_seconds = next(parameters.cpu_load_seq)
                shared.load_cpu(cpu_seconds)

            tasks = [chunk_of_work() for _ in range(parameters.io_number)]
            await asyncio.gather(*tasks)

        body = parameters.response_content
        return web.Response(body=body)


async def stats_reporter():
    while True:
        shared.report_stats()
        await asyncio.sleep(60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backend-ports', type=str, default='8080',
                        help='Comma separated ports where backend is listen on')
    parser.add_argument('-p', '--port', type=int, default=8081,
                        help='The port to listen on')
    parser.add_argument('-o', '--stats-output', type=str, default='asyncio.log',
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
    server = Server(backend_addresses=backend_addresses)
    app = web.Application()
    app.add_routes([
        web.get('/no-io', server.no_io),
        web.get('/sequential-io', server.sequential_io),
        web.get('/parallel-io', server.parallel_io),
    ])
    loop = asyncio.get_event_loop()
    loop.create_task(stats_reporter())
    web.run_app(app, port=args.port)


if __name__ == '__main__':
    main()
