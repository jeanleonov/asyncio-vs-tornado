import asyncio

from aiohttp import web

import shared


async def simulate_backend(request):
  # Provide content if requested
  response_file = request.query.get('response_file')
  if response_file:
    try:
      content = shared.RESPONSE_FILES[response_file]
    except KeyError:
      raise web.HTTPNotFound(reason='File not found')
  else:
    content = ''

  # Wait a bit if requested
  duration_str = request.query.get('duration', '0')
  try:
    duration = float(duration_str)
    assert duration >= 0.0
  except (TypeError, ValueError, AssertionError):
    raise web.HTTPBadRequest(reason='Parameter duration should be float')
  await asyncio.sleep(duration)

  # Respond
  return web.Response(body=content)


def main():
  app = web.Application()
  app.add_routes([web.get('/simulate-backend', simulate_backend)])
  web.run_app(app, port=8080)


if __name__ == '__main__':
  main()
