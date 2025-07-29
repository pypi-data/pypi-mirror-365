# xmodules/runner.py

import asyncio
from xmodules.session import create_or_load_session
from xmodules.handlers.save import register_save_handler


def run(api_id: int, api_hash: str, admin_id: int):
    """
    XModulesni ishga tushirish.
    """

    async def main():
        client = await create_or_load_session(api_id, api_hash)
        register_save_handler(client, admin_id=admin_id)
        await client.start()
        print(f"✅ XModules ishga tushdi.")
        await client.run_until_disconnected()

    asyncio.run(main())
