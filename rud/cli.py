from .downloader import Downloader, Post
import asyncio
import sys
import os
import argparse
from pfedit import Writable
from typing import Dict

skip_downloaded = True
skip_skipped = False

try:
    from . import downloaded
    downloaded = Writable(downloaded)
except ImportError:
    with open(os.path.dirname(__file__)+'/downloaded.py', 'w') as f:
        f.write(f"")
    from . import downloaded
    downloaded = Writable(downloaded)
    downloaded.posts: Dict[str, bool] = {}
    
try:
    from . import config
except ImportError:
    with open(os.path.dirname(__file__)+'/config.py', 'w') as f:
        f.write(f"cid = \"None\"\ncsec = \"None\"")
    from . import config

class NoAuth(Exception):
    pass

async def callback(post: Post):
    if skip_downloaded:
        if downloaded.posts.get(post.id) == True:
            return False
    
    if skip_skipped:
        if downloaded.posts.get(post.id) == False:
            return False

    os.system('cls')
    print(f"{post.title}\n|\n{post.src}  /  {post.url}\n|\n{post.subreddit}")
    b = await asyncio.get_event_loop().run_in_executor(None, input, 'download? (y/n)\n')
    b = b.lower()
    if b.startswith('n'):
        b = False
        downloaded.posts = dict(**downloaded.posts, **{post.id: False})
    elif b.startswith('y'):
        b = True
        downloaded.posts = dict(**downloaded.posts, **{post.id: True})
    else:
        print('unexpected input, quiting.')
        sys.exit(0)
    return b
    
def main():
    global skip_downloaded
    global skip_skipped
    args = collect_args().parse_args()
    if args.f:
        with open(os.path.dirname(__file__)+'/config.py', 'w') as f:
            f.write(f"cid = \"{args.f[0]}\"\ncsec = \"{args.f[1]}\"")
        return

    cid = args.cid or config.cid
    csec = args.csec or config.csec

    skip_downloaded = args.sd or skip_downloaded
    skip_skipped = args.snd or skip_skipped

    if cid == None or csec == None:
        raise NoAuth("No authorization provided, either fill out config.py in the libs directory, or pass `--cid` and `--csec`")

    dl = Downloader(cid, csec)
    if args.a == False:
        dl.callback = callback
    asyncio.run(dl.run(args.u))

def collect_args():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', type=str, nargs=2, help="takes {cid} and {csec}, saves them to the library's config.py")

    group.add_argument('-u', type=str, help="u/ of the desired account (do not include the `u/` part).")

    parser.add_argument('-a', type=bool, required=False, default=False, help="When true, skips the callback and downloads ALL posts")
    parser.add_argument('--cid', type=str, required=False, help="client id to authenticate with.")
    parser.add_argument('--csec', type=str, required=False, help="client secret to authenticate with.")
    parser.add_argument('--sd', type=bool, required=False, help="when true, skip previously downloaded posts.")
    parser.add_argument('--snd', type=bool, required=False, help="when true, skip previously skipped posts.")

    return parser


if __name__ == "__main__":
    main()