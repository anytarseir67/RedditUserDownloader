from .downloader import Downloader, Post
from . import config
import asyncio
import sys
import os
import argparse

class NoAuth(Exception):
    pass

async def callback(post: Post):
    os.system('cls')
    print(f"{post.title}\n|\n{post.src}  /  {post.url}\n|\n{post.subreddit}")
    b = await asyncio.get_event_loop().run_in_executor(None, input, 'download? (y/n)\n')
    b = b.lower()
    if b.startswith('n'):
        b = False
    elif b.startswith('y'):
        b = True
    else:
        print('unexpected input, quiting.')
        sys.exit(0)
    return b
    
def main(args):
    if args.f:
        with open(os.path.dirname(__file__)+'/config.py', 'w') as f:
            f.write(f"cid = \"{args.f[0]}\"\ncsec = \"{args.f[1]}\"")
        return

    cid = args.cid or config.cid
    csec = args.csec or config.csec

    if cid == None or csec == None:
        raise NoAuth("No authorization provided, either fill out config.py in the libs directory, or pass `--cid` and `--csec`")

    dl = Downloader(cid, csec)
    if args.a == False:
        dl.callback = callback
    asyncio.run(dl.run(args.u))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', type=str, nargs=2, help="takes {cid} and {csec}, saves them to the library's config.py")

    group.add_argument('-u', type=str, help="u/ of the desired account (do not include the `u/` part).")

    parser.add_argument('-a', type=bool, required=False, default=False, help="When true, skips the callback and downloads ALL posts")
    parser.add_argument('--cid', type=str, required=False, help="client id to authenticate with.")
    parser.add_argument('--csec', type=str, required=False, help="client secret to authenticate with.")

    args = parser.parse_args()

    main(args)