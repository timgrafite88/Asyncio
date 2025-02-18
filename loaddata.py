import asyncio
import datetime

import more_itertools
import requests
from aiohttp import ClientSession

from migrate import Session, StarWars, close_orm, int_orm


async def get_people(person_id: int, client: ClientSession):
    response = await client.get(f"https://swapi.py4e.com/api/people/{person_id}/")
    json_data = await response.json()
    return json_data

def transform_character_data(character):
    transformed_data = {
        'id': character['url'].split('/')[-2],
        'birth_year': character['birth_year'],
        'eye_color': character['eye_color'],
        'films': ','.join([requests.get(film).json()['title'] for film in character['films']]) if len(character['films']) != 0 else '',
        'gender': character['gender'],
        'hair_color': character['hair_color'],
        'height': int(character['height']),
        'homeworld': ','.join(requests.get(character['homeworld']).json()['name']) if len(character['homeworld']) != 0 else '',
        'mass': float(character['mass']) if character['mass'] != 'unknown' else None,
        'name': character['name'],
        'skin_color': character['skin_color'],
        'species': ','.join([requests.get(specie).json()['name'] for specie in character['species']]) if len(character['species']) != 0 else '',
        'starships': ','.join([requests.get(starship).json()['name'] for starship in character['starships']]) if len(character['starships']) != 0 else '',
        'vehicles': ','.join([requests.get(vehicle).json()['name'] for vehicle in character['vehicles']]) if len(character['vehicles']) != 0 else ''
    }
    return transformed_data

async def insert_people(people_list: list[dict]):
    async with Session() as session:
        orm_objs = [transform_character_data(item) for item in people_list]
        session.add_all(orm_objs)
        await session.commit()


MAX_REQUEST_SIZE = 5


async def main():
    await int_orm()
    async with ClientSession() as client:
        for people_ids in more_itertools.chunked(range(1, 100), MAX_REQUEST_SIZE):
            coros = [get_people(i, client) for i in people_ids]
            result = await asyncio.gather(*coros)
            insert_people_couroutine = insert_people(result)
            asyncio.create_task(insert_people_couroutine)
    tasks = asyncio.all_tasks()
    current_task = asyncio.current_task()
    tasks.remove(current_task)
    for task in tasks:
        await task
    await close_orm()


start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)