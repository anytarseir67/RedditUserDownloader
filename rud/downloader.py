import asyncpraw
from functools import cached_property
import aiohttp
import aiofiles
from aiofiles import os as aos
import os
import asyncio
class Post:
    def __init__(self, src: str, url: str, title: str, subreddit: str):
        self.src = src
        self.url = 'https://www.reddit.com' + url
        self.title = title
        self.subreddit = subreddit
    
class Downloader:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    async def callback(self, post: Post) -> bool:
        """
        overwrite to return false when you don't want to download a given post
        """
        return True

    async def download(self, post: Post, name: str) -> None:
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession()
        
        urls = []

        if hasattr(post, 'gallery_data'):
            print('gallery')
            async with self.session.get(post.url+'.json') as resp:
                dat = await resp.json()
            ids = [i['media_id'] for i in post.gallery_data['items']]
            for id in ids:
                url = dat[0]['data']['children'][0]['media_metadata'][id]['p'][0]['u']
                urls.append(url.split("?")[0].replace("preview", "i"))
                
        else:
            urls = [post.src]

        try:
            await aos.mkdir(f'./{name}')
        except FileExistsError:
            pass

        for i, url in enumerate(urls):
            print(url)
            _ = '.' + url.split('.')[-1].split('/')[0]
            ext = _ or 'png'
            num = str(i) if i != 0 else ''
            filename = f'./{name}/' + ''.join(x for x in post.title.replace(' ', '-') if x.isalnum() or x == '-')+num+ext
            if os.path.exists(filename) == True:
                return
            async with self.session.get(url) as resp:
                dat = await resp.read()
            async with aiofiles.open(filename, 'wb') as f:
                await f.write(dat)

    async def get_posts(self, name: str) -> Post:
        user = await self.reddit.redditor(name)
        async for post in user.stream.submissions(pause_after=10):
            if post == None:
                break
            await post.load()
            await post.subreddit.load()
            yield Post(post.url, post.permalink, post.title, post.subreddit.display_name)

    async def main(self, name: str) -> None:
        self.reddit = asyncpraw.Reddit(client_id=self._client_id, client_secret=self._client_secret, user_agent=f"RedditUserDownloader")
        async for post in self.get_posts(name):
            if await self.callback(post) == True:
                asyncio.create_task(self.download(post, name))