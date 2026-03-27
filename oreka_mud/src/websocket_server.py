"""
WebSocket server for OrekaMUD3.
Runs alongside the telnet server. Veil Client connects via WebSocket.
Proxies bidirectionally to the internal telnet server.
"""
import asyncio
import logging

logger = logging.getLogger("OrekaMUD.WebSocket")

WS_PORT = 8765
WS_HOST = '0.0.0.0'


async def ws_handler(websocket):
    """Handle a WebSocket connection by proxying to the telnet MUD."""
    logger.info(f"WebSocket connection from {websocket.remote_address}")

    try:
        # Connect to the local telnet server
        reader, writer = await asyncio.open_connection('127.0.0.1', 4000)

        async def client_to_mud():
            """Forward WebSocket messages to MUD telnet."""
            try:
                async for message in websocket:
                    if isinstance(message, str):
                        writer.write((message + '\r\n').encode('utf-8'))
                    else:
                        writer.write(message + b'\r\n')
                    await writer.drain()
            except Exception:
                pass
            finally:
                writer.close()

        async def mud_to_client():
            """Forward MUD telnet output to WebSocket."""
            try:
                while True:
                    data = await reader.read(4096)
                    if not data:
                        break
                    # Strip telnet negotiation bytes for WebSocket clients
                    clean = _strip_telnet_negotiation(data)
                    if clean:
                        text = clean.decode('utf-8', errors='replace')
                        await websocket.send(text)
            except Exception:
                pass

        # Run both directions concurrently
        done, pending = await asyncio.wait(
            [asyncio.create_task(client_to_mud()),
             asyncio.create_task(mud_to_client())],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
    finally:
        logger.info(f"WebSocket connection closed from {websocket.remote_address}")


def _strip_telnet_negotiation(data):
    """Remove IAC sequences from telnet data for WebSocket clients."""
    IAC = 255
    result = bytearray()
    i = 0
    while i < len(data):
        if data[i] == IAC and i + 1 < len(data):
            cmd = data[i + 1]
            if cmd in (251, 252, 253, 254):  # WILL, WONT, DO, DONT
                i += 3  # Skip IAC + cmd + option
                continue
            elif cmd == 250:  # SB (subnegotiation)
                # Skip until IAC SE
                j = i + 2
                while j < len(data) - 1:
                    if data[j] == IAC and data[j + 1] == 240:  # IAC SE
                        j += 2
                        break
                    j += 1
                i = j
                continue
            elif cmd == IAC:  # Escaped IAC
                result.append(IAC)
                i += 2
                continue
            else:
                i += 2
                continue
        result.append(data[i])
        i += 1
    return bytes(result)


async def start_websocket_server():
    """Start the WebSocket server. Call from main.py."""
    try:
        import websockets
        async with websockets.serve(ws_handler, WS_HOST, WS_PORT):
            logger.info(f"WebSocket server started on {WS_HOST}:{WS_PORT}")
            await asyncio.Future()  # Run forever
    except ImportError:
        logger.warning("websockets package not installed — WebSocket server disabled. Install with: pip install websockets")
    except Exception as e:
        logger.error(f"WebSocket server failed to start: {e}")
