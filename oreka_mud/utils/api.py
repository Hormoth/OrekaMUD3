from aiohttp import web

class OrekaServer:
    def __init__(self, world):
        self.world = world
        self.app = web.Application()
        self.app.router.add_get("/who", self.handle_who)

    async def handle_who(self, request):
        return web.json_response([{"name": p.name, "race": p.race} for p in self.world.players])
