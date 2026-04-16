"""
WebSocket server for OrekaMUD3.
Runs alongside the telnet server. Veil Client connects via WebSocket.
Proxies bidirectionally to the internal telnet server.

GMCP Integration:
  - Telnet IAC SB 201 ... IAC SE sequences are extracted from the MUD output
    stream and re-sent to the WebSocket client as text frames:
        GMCP:<package> <json>
  - WebSocket client GMCP messages (prefixed with "GMCP:") are converted to
    telnet subnegotiation and forwarded to the MUD.
"""
import asyncio
import logging

logger = logging.getLogger("OrekaMUD.WebSocket")

WS_PORT = 8765
WS_HOST = '127.0.0.1'

# Telnet bytes used for GMCP extraction
IAC = 255
SB = 250
SE = 240
WILL = 251
WONT = 252
DO = 253
DONT = 254
GMCP_OPT = 201


def _extract_gmcp_and_clean(data):
    """Parse raw telnet data, extract GMCP subnegotiations, and return
    (clean_bytes, list_of_gmcp_strings).

    GMCP payloads are returned as strings like "Char.Vitals {...}" ready
    to prefix with "GMCP:" for WebSocket delivery.
    """
    gmcp_messages = []
    result = bytearray()
    i = 0
    while i < len(data):
        if data[i] == IAC and i + 1 < len(data):
            cmd = data[i + 1]
            if cmd == SB and i + 2 < len(data) and data[i + 2] == GMCP_OPT:
                # GMCP subnegotiation: IAC SB 201 <payload> IAC SE
                j = i + 3
                payload_start = j
                while j < len(data) - 1:
                    if data[j] == IAC and data[j + 1] == SE:
                        payload = data[payload_start:j]
                        try:
                            gmcp_messages.append(payload.decode('utf-8', errors='replace'))
                        except Exception:
                            pass
                        j += 2
                        break
                    j += 1
                else:
                    # Incomplete subnegotiation — skip to end
                    j = len(data)
                i = j
                continue
            elif cmd in (WILL, WONT, DO, DONT):
                i += 3  # Skip IAC + cmd + option
                continue
            elif cmd == SB:
                # Non-GMCP subnegotiation — skip until IAC SE
                j = i + 2
                while j < len(data) - 1:
                    if data[j] == IAC and data[j + 1] == SE:
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
    return bytes(result), gmcp_messages


def _gmcp_to_telnet_sb(package_and_data):
    """Convert a GMCP string (e.g. 'Core.Hello {...}') to IAC SB 201 ... IAC SE."""
    payload = package_and_data.encode('utf-8')
    return bytes([IAC, SB, GMCP_OPT]) + payload + bytes([IAC, SE])


# =========================================================================
# Veil Pre-Auth Wizard — runs before opening telnet proxy
# =========================================================================

VEIL_BANNER = """
\033[1;35m
 ╔══════════════════════════════════════════════════════════════╗
 ║                                                              ║
 ║                    V E I L   C L I E N T                     ║
 ║                                                              ║
 ║              Step through the Veil. Oreka waits.             ║
 ║                                                              ║
 ╚══════════════════════════════════════════════════════════════╝
\033[0m
  An entry portal to the world of OrekaMUD3.
  For NPC Chat or Character Sheet, use the Veil Portal (oreka_veil_portal.html).

"""


async def _recv_line(websocket, timeout=120):
    """Receive a single line of text from the WebSocket client."""
    try:
        msg = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8', errors='replace')
        return msg
    except (asyncio.TimeoutError, Exception):
        return None


def _format_npc_menu(npcs):
    if not npcs:
        return "\nNo chat-eligible NPCs configured.\n  > "
    lines = ["\n\033[1;36m  Choose an NPC to dream with:\033[0m\n"]
    for i, npc in enumerate(npcs, 1):
        room = f" — {npc['room']}" if npc.get('room') else ""
        lines.append(f"    \033[1;33m{i}.\033[0m {npc['name']}{room}")
    lines.append("\n  > ")
    return "\n".join(lines)


async def _veil_preauth(websocket):
    """Run the Veil pre-auth wizard.

    Returns (auth_dict, error_message). On success, auth_dict contains:
      - username (str)
      - password (str)
      - is_new (bool)
      - mode ('mud' or 'chat')
      - chat_npc_vnum (int or None)
      - chat_npc_name (str or None)
    """
    from src.veil_auth import (
        validate_password, is_allowed, can_signup, character_exists,
        list_chat_npcs, get_default_chat_npc,
    )

    await websocket.send(VEIL_BANNER)

    # Existing or new?
    await websocket.send("\n  Do you have an existing character? (y/n): ")
    resp = await _recv_line(websocket)
    if not resp:
        return None, "Connection closed."
    is_new = resp.strip().lower().startswith('n')

    username = None
    password = None

    if is_new:
        if not can_signup():
            return None, "\n\033[1;31m  [X] New character creation is disabled on Veil.\033[0m\n  Contact an administrator.\n"
        await websocket.send("\n\033[1;32m  [+] Creating new character. The MUD will guide you.\033[0m\n")
    else:
        # Existing character flow
        await websocket.send("\n  Username: ")
        username = (await _recv_line(websocket) or "").strip()
        if not username:
            return None, "\n  No username provided.\n"

        await websocket.send("  Password: ")
        password = (await _recv_line(websocket) or "").strip()
        if not password:
            return None, "\n  No password provided.\n"

        # Validate password
        valid, reason = validate_password(username, password)
        if not valid:
            return None, f"\n\033[1;31m  [X] {reason}\033[0m\n"

        # Check whitelist
        allowed, reason = is_allowed(username)
        if not allowed:
            return None, f"\n\033[1;31m  [X] {reason}\033[0m\n"

        await websocket.send(f"\n\033[1;32m  [+] Welcome back, {username}.\033[0m\n")

    # Go straight to MUD — NPC Chat is handled by the Veil Portal
    mode = 'mud'
    chat_npc_vnum = None
    chat_npc_name = None
    await websocket.send("\n\033[1;32m  [+] Entering OrekaMUD...\033[0m\n\n")

    return {
        "username": username,
        "password": password,
        "is_new": is_new,
        "mode": mode,
        "chat_npc_vnum": chat_npc_vnum,
        "chat_npc_name": chat_npc_name,
    }, None


# =========================================================================
# Main WebSocket handler
# =========================================================================

async def ws_handler(websocket):
    """Handle a WebSocket connection by proxying to the telnet MUD.

    GMCP subnegotiation from the MUD is intercepted and forwarded as
    ``GMCP:<package> <json>`` text frames to the WebSocket client.
    """
    logger.info(f"WebSocket connection from {websocket.remote_address}")

    writer = None
    try:
        # === PHASE 1: Veil Pre-Auth Wizard ===
        auth, error = await _veil_preauth(websocket)
        if error:
            try:
                await websocket.send(error + "\n  Closing connection.\n")
            except Exception:
                pass
            await asyncio.sleep(2)
            return
        if not auth:
            return

        # === PHASE 2: Open telnet proxy ===
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection('127.0.0.1', 4000),
            timeout=10.0,
        )

        # Send DO GMCP to tell the MUD server we support GMCP
        writer.write(bytes([IAC, DO, GMCP_OPT]))
        await writer.drain()

        # === PHASE 3: Auto-login ===
        # The telnet server will prompt: "Do you have an existing character? (y/n): "
        # then "Enter your character name:" then "Enter your password:"
        # We auto-fill these for existing characters. New characters fall through.
        autologin_complete = asyncio.Event()
        chat_command_sent = [False]  # mutable for closure

        async def _autologin():
            """Send credentials to the telnet server when prompted."""
            try:
                await asyncio.sleep(0.3)  # let banner render
                if not auth["is_new"]:
                    # Existing character: y, name, password
                    writer.write(b"y\r\n")
                    await writer.drain()
                    await asyncio.sleep(0.2)
                    writer.write((auth["username"] + "\r\n").encode("utf-8"))
                    await writer.drain()
                    await asyncio.sleep(0.2)
                    writer.write((auth["password"] + "\r\n").encode("utf-8"))
                    await writer.drain()
                else:
                    # New character: send "n" and let telnet handle creation
                    writer.write(b"n\r\n")
                    await writer.drain()
                # Wait for login to settle
                await asyncio.sleep(2.5)
                autologin_complete.set()

                # If chat mode, send the chat command
                if auth["mode"] == "chat" and auth["chat_npc_vnum"]:
                    # Use the NPC's first name token for matching
                    npc_query = (auth["chat_npc_name"] or "").split()[0] if auth.get("chat_npc_name") else ""
                    if npc_query:
                        writer.write(f"chat {npc_query}\r\n".encode("utf-8"))
                        await writer.drain()
                        chat_command_sent[0] = True
            except Exception as e:
                logger.error(f"Auto-login error: {e}")

        autologin_task = asyncio.create_task(_autologin())

        async def client_to_mud():
            """Forward WebSocket messages to MUD telnet (after auto-login)."""
            try:
                # Wait for auto-login to complete before accepting client input
                # so user input doesn't race with autofilled credentials
                await autologin_complete.wait()
                async for message in websocket:
                    if isinstance(message, str):
                        # Check for GMCP messages from WebSocket client
                        if message.startswith("GMCP:"):
                            # Convert to telnet GMCP subnegotiation
                            gmcp_payload = message[5:]  # Strip "GMCP:"
                            sb_bytes = _gmcp_to_telnet_sb(gmcp_payload)
                            writer.write(sb_bytes)
                        else:
                            writer.write((message + '\r\n').encode('utf-8'))
                    else:
                        writer.write(message + b'\r\n')
                    await writer.drain()
            except Exception:
                pass

        async def mud_to_client():
            """Forward MUD telnet output to WebSocket.

            Intercepts GMCP subnegotiation bytes and sends them as
            GMCP:-prefixed text frames instead of raw telnet bytes.
            Buffers partial IAC sequences across read boundaries.
            """
            pending = bytearray()
            try:
                while True:
                    data = await reader.read(4096)
                    if not data:
                        break

                    # Prepend any leftover bytes from a split IAC sequence
                    if pending:
                        data = bytes(pending) + data
                        pending.clear()

                    # Check if data ends mid-IAC sequence (incomplete subneg)
                    # Look for IAC SB without matching IAC SE
                    i = len(data) - 1
                    while i >= 0 and data[i] != IAC:
                        i -= 1
                    if i >= 0 and i < len(data) - 1:
                        cmd = data[i + 1]
                        if cmd == SB:
                            # IAC SB started but no IAC SE found after it
                            has_se = False
                            for j in range(i + 2, len(data) - 1):
                                if data[j] == IAC and data[j + 1] == SE:
                                    has_se = True
                                    break
                            if not has_se:
                                # Buffer the incomplete sequence for next read
                                pending.extend(data[i:])
                                data = data[:i]
                    elif i == len(data) - 1:
                        # Data ends with lone IAC byte — buffer it
                        pending.append(data[i])
                        data = data[:i]

                    if not data:
                        continue

                    # Extract GMCP messages and clean telnet negotiation
                    clean, gmcp_messages = _extract_gmcp_and_clean(data)

                    # Send any GMCP messages as prefixed text frames
                    for gmcp_msg in gmcp_messages:
                        try:
                            await websocket.send(f"GMCP:{gmcp_msg}")
                        except Exception:
                            pass

                    # Send clean text output
                    if clean:
                        text = clean.decode('utf-8', errors='replace')
                        await websocket.send(text)
            except Exception:
                pass

        # Run both directions concurrently
        tasks = [
            asyncio.create_task(client_to_mud()),
            asyncio.create_task(mud_to_client()),
        ]
        try:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
    finally:
        # Clean up TCP connection
        if writer:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        # Close WebSocket
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info(f"WebSocket connection closed from {websocket.remote_address}")


async def start_websocket_server():
    """Start the WebSocket server. Call from main.py."""
    try:
        import websockets
        async with websockets.serve(
            ws_handler, WS_HOST, WS_PORT,
            ping_interval=30,
            ping_timeout=10,
            close_timeout=5,
        ):
            logger.info(f"WebSocket server started on {WS_HOST}:{WS_PORT}")
            await asyncio.Future()  # Run forever
    except ImportError:
        logger.warning("websockets package not installed — WebSocket server disabled. Install with: pip install websockets")
    except Exception as e:
        logger.error(f"WebSocket server failed to start: {e}")
