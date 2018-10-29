import time
import asyncio

async def say_after(delay, message):
    await asyncio.sleep(delay)
    print(message)

async def main():
    print(f"started: {time.strftime('%X')}")
    await say_after(1, "Hello, ...")
    print(f"middle: {time.strftime('%X')}")
    await say_after(2, "...world!")
    print(f"finished: {time.strftime('%X')}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
