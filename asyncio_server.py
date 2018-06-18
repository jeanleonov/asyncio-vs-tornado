import asyncio

import aiohttp
from aiohttp import web

import shared


class Parameters(object):
    def __init__(self, request):
        # All parameters accepts one of: missing, tiny, small, normal, big, huge
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
    def __init__(self, backend_address):
        self.backend_address = backend_address

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
                url = f'{self.backend_address}/simulate-backend'
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
                url = f'{self.backend_address}/simulate-backend'
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
    server = Server('http://localhost:8080')
    app = web.Application()
    app.add_routes([
        web.get('/no-io', server.no_io),
        web.get('/sequential-io', server.sequential_io),
        web.get('/parallel-io', server.parallel_io),
    ])
    loop = asyncio.get_event_loop()
    loop.create_task(stats_reporter())
    web.run_app(app, port=8081)


if __name__ == '__main__':
    main()
