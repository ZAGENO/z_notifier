import asyncio


def ensure_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        return event_loop
