import os
import threading

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from aiohttp import web, ClientSession
import asyncio


class AsyncFileStorage:

    def __init__(self):
        with open("config.yaml", "r") as r:
            stream = r.read()
        self._config = load(stream, Loader=Loader)
        self._host = self._config['host']
        self._port = self._config['port']
        self._dir = self._config['dir']
        self._nodes = self._config['nodes']
        self._save_from_other_nodes = self._config['save_from_other_nodes']

    async def _find(self, request):
        file = request.match_info.get('file')
        if file in os.listdir(self._dir):
            thread = threading.Thread(target=self._read_file, args=(file, ))
            thread.start()
            thread.join()
            return web.Response(text=self.read_response)
        else:
            thread = threading.Thread(target=self._async_find, args=(file, ))
            thread.start()
            thread.join()
            if self.friendly_find_response:
                return web.Response(text=self.friendly_find_response)
            raise web.HTTPNotFound()

    async def _find_silently(self, request):
        file = request.match_info.get('file')
        if file in os.listdir(self._dir):
            thread = threading.Thread(target=self._read_file, args=(file, ))
            thread.start()
            thread.join()
            return web.Response(text=self.read_response)
        else:
            return web.Response(text='False')

    def _async_find(self, file):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = asyncio.gather(*[self._ask_nodes(
            "http://{}:{}/find_silently/{}".format(node['host'], node['port'], file))
            for node in self._nodes.values()])
        responses = loop.run_until_complete(tasks)
        loop.close()
        self.friendly_find_response = None
        for response in responses:
            if response != 'False':
                if self._save_from_other_nodes:
                    thread = threading.Thread(target=self._save_file, args=(file, ))
                    thread.start()
                    thread.join()
                self.friendly_find_response = response

    @staticmethod
    async def _fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def _ask_nodes(self, url):
        async with ClientSession() as session:
            return await self._fetch(session, url)

    def _read_file(self, file):
        with open(os.path.join(self._dir, file), "r") as r:
            self.read_response = r.read()

    def _save_file(self, file):
        with open(os.path.join(self._dir, file), "w") as w:
            w.write(file)

    def _write_file(self):
        pass

    def run(self):
        app = web.Application()
        app.add_routes([
            web.get('/{file}', self._find),
            web.get('/find_silently/{file}', self._find_silently),
        ])
        web.run_app(app, host=self._host, port=int(self._port))


a = AsyncFileStorage()
a.run()
