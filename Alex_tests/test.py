import websockets, asyncio

async def test_server():
    try:
        async with websockets.connect("wss://vital-mastiff-publicly.ngrok-free.app") as ws:
            return True
    except Exception as e:
        print(e)
        return False
    
print(asyncio.run(test_server()))
