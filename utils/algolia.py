import json
import requests

import aiohttp

from classes.algolia import AlgoliaResult


class AlgoliaUtil:

    def __init__(self, app: str, key: str, index_name: str) -> None:
        self.app = app
        self.key = key
        self.index_name = index_name

        self.base_url = 'https://{}-dsn.algolia.net{}'
        self.headers = {
            'X-Algolia-Application-Id': self.app,
            'X-Algolia-API-Key': self.key
        }

    async def _get_data(self, path: str, data: dict[str, str | int]):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    self.base_url.format(self.app, path),
                    headers=self.headers,
                    json=data,
            ) as ans:
                return await ans.json()

    async def search_query(self, query: str) -> list[AlgoliaResult]:
        ans = await self._get_data(f'/1/indexes/{self.index_name}/query', {
            'query': query,
            'hitsPerPage': 5,
        })

        return [
            AlgoliaResult(
                url=i['url'],
                description=i['content'],
                heading=i['hierarchy']['lvl1'],
            ) for i in ans['hits']
        ]


# ans = requests.post(
#     BASE.format(app, f'/1/indexes/{index_name}/query'),
#     headers=headers,
#     json={
#         'query': 'contributing',
#         'hitsPerPage': 5,
#         # 'getRankingInfo': 1,
#         # 'distinct': 1,
#     })

# with open('out.json', 'w', encoding='utf-8') as f:
#     json.dump(ans.json(), f, indent=4)

# for i in ans.json()['hits']:
#     print(i['url'], i['content'], i['hierarchy']['lvl1'],
#           i['_highlightResult']['hierarchy']['lvl1']['value'])
