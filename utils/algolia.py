# import requests

from typing import Tuple
import aiohttp

from classes.algolia import AlgoliaResult, AlgoliaResultType
from bs4 import BeautifulSoup


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
                    json={
                        **data,
                        'highlightPreTag':
                        '***__',
                        'highlightPostTag':
                        '__***',
                        'attributesToRetrieve': [
                            'hierarchy.lvl0', 'hierarchy.lvl1',
                            'hierarchy.lvl2', 'content', 'type', 'url'
                        ],
                        'attributesToSnippet': [
                            'hierarchy.lvl0:10', 'hierarchy.lvl1:10',
                            'hierarchy.lvl2:10', 'hierarchy.lvl6:10',
                            'content:10'
                        ],
                        'snippetEllipsisText':
                        '...',
                    },
            ) as ans:
                return await ans.json()

    async def search_query(self,
                           query: str,
                           max: int = 5) -> list[AlgoliaResult]:
        ans = await self._get_data(
            f'/1/indexes/{self.index_name}/query',
            {
                'query': query,
                'hitsPerPage': min(max, 5),
            },
        )

        out = []
        for i in ans['hits']:
            if i['type'] == 'lvl1':
                # lvl1 is header and there is no description given
                out.append(
                    AlgoliaResult(
                        header=i['_snippetResult']['hierarchy']['lvl1']
                        ['value'],
                        description=None,
                        highlight=i['_highlightResult']['hierarchy']['lvl1']
                        ['matchedWords'],
                        url=i['url'],
                        type=AlgoliaResultType.mainHeader,
                    ))
            elif i['type'] == 'lvl2':
                # lvl1 is description and lvl2 is header
                out.append(
                    AlgoliaResult(
                        header=i['_snippetResult']['hierarchy']['lvl2']
                        ['value'],
                        description=i['_snippetResult']['hierarchy']['lvl1']
                        ['value'],
                        highlight=i['_highlightResult']['hierarchy']['lvl2']
                        ['matchedWords'],
                        url=i['url'],
                        type=AlgoliaResultType.subHeader,
                    ))

            elif i['type'] == 'content':
                # lvl1 is description and content is header
                out.append(
                    AlgoliaResult(
                        header=i['_snippetResult']['content']['value'],
                        description=i['_snippetResult']['hierarchy']['lvl1']
                        ['value'],
                        highlight=i['_highlightResult']['content']
                        ['matchedWords'],
                        url=i['url'],
                        type=AlgoliaResultType.content,
                    ))

        return out

    async def get_metadata(self,
                           url: str) -> Tuple[str, str, str, str, str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as ans:
                soup = BeautifulSoup(await ans.read(), 'html.parser')
                title: str = soup.find(
                    'meta',
                    attrs={
                        'name': 'og:title'
                    },
                ).get('content')  # type: ignore

                description: str = soup.find(
                    'meta',
                    attrs={
                        'name': 'og:description'
                    },
                ).get('content')  # type: ignore

                image: str = soup.find(
                    'meta',
                    attrs={
                        'name': 'og:image'
                    },
                ).get('content')  # type: ignore

                image_alt: str = soup.find(
                    'meta',
                    attrs={
                        'name': 'og:image:alt'
                    },
                ).get('content')  # type: ignore

                site: str = soup.find(
                    'meta',
                    attrs={
                        'name': 'og:site_name'
                    },
                ).get('content')  # type: ignore

                url_full: str = soup.find(
                    'meta',
                    attrs={
                        'name': 'og:url'
                    },
                ).get('content')  # type: ignore

                return title, description, image, image_alt, site, url_full


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
