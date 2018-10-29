import time
import asyncio

async def say_after(delay, message):
    await asyncio.sleep(delay)
    print(message)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(
        say_after(3, "Hello, ..."),
        say_after(2, "...world!")
    ))
loop.close()
