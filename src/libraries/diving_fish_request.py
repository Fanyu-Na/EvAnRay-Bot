from typing import Optional, Dict, List, Tuple
import aiohttp
import asyncio

async def get_player_best_50(payload: Dict):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        print(await resp.json())
        return resp
    
async def get_player_plate_data(payload: Dict):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload) as resp:
        result = await resp.json()
        return result


# asyncio.run(get_player_best_50({"username":"ryannn"}))