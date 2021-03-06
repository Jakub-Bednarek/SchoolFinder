import sys
import asyncio

from app import App


async def main():
    app = App()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
