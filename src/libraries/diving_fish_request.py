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
        print(result)
        return result

async def get_rating_ranking():
    async with aiohttp.request("get", 'https://www.diving-fish.com/api/maimaidxprober/rating_ranking') as resp:
        result = await resp.json()
        return result
    
async def get_user_name_by_tentcent_user_id(payload: Dict):
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return 400, ""
        elif resp.status == 403:
            return 403, ""
        elif resp.status == 200:
            result = await resp.json()
            username = str(result['username'])
            return 200, username
        else:
            return -1,""



# asyncio.run(get_player_best_50({"username":"ryan"}))