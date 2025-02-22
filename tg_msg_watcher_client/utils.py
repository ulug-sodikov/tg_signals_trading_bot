import aiohttp


async def async_post_request(url, json):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.post(url, json=json) as response:
            return response.ok
