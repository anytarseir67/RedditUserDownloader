import asyncpraw
import aiohttp
import aiofiles
from aiofiles import os as aos
import os
import asyncio
from asyncprawcore import ResponseException

class ConnectionFailed(Exception):
    """raised when reddit responds in an unexpected way.

    Parameters
    ----------
    Exception: :class:`str`
        description of the exception.
    """
    pass

class Post:
    """class contaning information for a given post.

    Attributes
    -----------
    src: :class:`str`
        source url of the post. (typically ``i.redd.it``)
    url: :class:`str`
        permalink to the post. (``reddit.com/r/...``)
    title: :class:`str`
        title of the post.
    subreddit: :class:`str`
        name of the subreddit this post belongs to.
    """
    def __init__(self, src: str, url: str, title: str, subreddit: str, _id: str):
        self.src = src
        self.url = 'https://www.reddit.com' + url
        self.title = title
        self.subreddit = subreddit
        self.id = _id
    
class Downloader:
    """class to facilitate downloading of a user's posts.

    Parameters
    ----------
    client_id: :class:`str`
        client id to connect with.
    client_secret: :class:`str`
        client secret to authenticate with.
    """
    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    async def auth(self, useragent: str) -> bool:
        """verify our connection to reddit.

        Parameters
        ----------
        useragent: :class:`str`
            the useragent that should be sent with out requests.

        Returns
        -------
        :class:`bool`
            return ``True`` when connection is successful, otherwise returns ``False``.
        """
        self.reddit = asyncpraw.Reddit(client_id=self._client_id, client_secret=self._client_secret, user_agent=useragent)
        try:
            await self.reddit.user.me()
        except ResponseException:
            return False
        return True

    async def callback(self, post: Post) -> bool:
        """method called to determine if the given post should be downloaded. (intended to be overwritten, defaults to always ``True``)

        Parameters
        ----------
        post: :class:`Post`
            post that will be downloaded.

        Returns
        -------
        :class:`bool`
            when ``True``, the post will be downloaded, when ``False`` the post will be skipped.
        """
        return True

    async def download(self, post: Post, name: str) -> None:
        """method that downloads the images related to a given post.

        Parameters
        ----------
        post: :class:`Post`
            the post to be downloaded.
        name: :class:`str`
            name of the output directory.
        """
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession()
        
        urls = []

        if hasattr(post, 'gallery_data'):
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
        """get all posts from a given user

        Parameters
        ----------
        name: :class:`str`
            name of the user who's posts will be fetched.

        Yields
        ------
        :class:`Post`
            one of the user's posts.
        """
        user = await self.reddit.redditor(name)
        async for post in user.stream.submissions(pause_after=10):
            if post == None:
                break
            await post.load()
            await post.subreddit.load()
            yield Post(post.url, post.permalink, post.title, post.subreddit.display_name, post.id)

    async def run(self, name: str) -> None:
        """main loop of the default implementation.

        Parameters
        ----------
        name: :class:`str`
            name of the user who's posts will be downloaded.
        
        Raises
        ------
        :exc:`ConnectionFailed`
            reddit did not respond the way we expect.
        """
        auth = await self.auth("RedditUserDownloader")
        if auth:
            async for post in self.get_posts(name):
                if await self.callback(post) == True:
                    asyncio.create_task(self.download(post, name))
        else:
            raise ConnectionFailed("reddit responded in an unexpected way. check your id / secret, and reddit's status.")