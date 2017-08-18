#!/bin/env python

import aiohttp


async def aio_get(url: str):
    async with aiohttp.ClientSession() as session:
<<<<<<< HEAD
        async with session.get(url, headers=headers) as r:
            if r.status == 200:
                return r.text()
            else:
                return None

async def aio_get_json(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            if r.status == 200:
                return r.json()
            else:
                return None
=======
    async with session.get(url) as r:
        if r.status == 200:
            return r
        else:
            return None
>>>>>>> parent of 6b6d243... progress on DDG cog & aiohttp wrapper
