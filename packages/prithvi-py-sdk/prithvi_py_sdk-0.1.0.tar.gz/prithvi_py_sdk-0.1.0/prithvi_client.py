import asyncio

class PrithviClient:
    def __init__(self, host='127.0.0.1', port=1902):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.auth_token = None
        self.retries = 5

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            print("Connected to Prithvi Server.")
            await self._skip_banner()
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def _skip_banner(self):
        # Skip any server startup junk (like "🚀 PrithviServer listening...")
        try:
            line = await asyncio.wait_for(self.reader.readline(), timeout=0.5)
            decoded = line.decode().strip()
            if decoded.startswith("🚀") or "listening" in decoded.lower():
                return
        except asyncio.TimeoutError:
            pass  # Server sent nothing

    async def _send_command(self, cmd):
        if not self.writer:
            raise ConnectionError("Client is not connected")

        try:
            self.writer.write((cmd + "\n").encode())
            await self.writer.drain()

            response = await self.reader.readline()
            return response.decode().strip()
        except Exception as e:
            raise RuntimeError(f"Failed to send command: {str(e)}")

    # ---------------------- Core Commands ----------------------

    async def set(self, key, value, expiry=None):
        cmd = f"SET {key} {value}" + (f" EX {expiry}" if expiry else "")
        return await self._send_command(cmd)

    async def get(self, key):
        return await self._send_command(f"GET {key}")

    async def del_key(self, key):
        return await self._send_command(f"DEL {key}")

    async def exists(self, key):
        return await self._send_command(f"EXISTS {key}")

    async def keys(self):
        return await self._send_command("KEYS")

    async def sadd(self, key, value):
        return await self._send_command(f"SADD {key} {value}")

    async def smembers(self, key):
        return await self._send_command(f"SMEMBERS {key}")

    async def srem(self, key, value):
        return await self._send_command(f"SREM {key} {value}")

    async def lpush(self, key, value):
        return await self._send_command(f"LPUSH {key} {value}")

    async def rpush(self, key, value):
        return await self._send_command(f"RPUSH {key} {value}")

    async def lpop(self, key):
        return await self._send_command(f"LPOP {key}")

    async def rpop(self, key):
        return await self._send_command(f"RPOP {key}")

    async def get_list(self, key):
        return await self._send_command(f"GETLIST {key}")

    async def flush(self, confirm=False):
        return await self._send_command("FLUSH FALL" if confirm else "FLUSH")

    async def save(self):
        return await self._send_command("SAVE")

    async def load(self):
        return await self._send_command("LOAD")

    async def quit(self):
        return await self._send_command("QUIT")

    async def help(self):
        return await self._send_command("HELP")

    # ---------------------- Auth ----------------------

    async def auth(self, username):
        response = await self._send_command(f"AUTH {username}")
        if response.startswith("TOKEN "):
            self.auth_token = response.split(" ")[1]
            return "Authentication successful. Token stored."
        raise ValueError(f"Unexpected response: {response}")

    async def token(self, hash=None):
        token_to_use = hash or self.auth_token
        if not token_to_use:
            raise ValueError("No token provided or stored. Run auth() first or pass token manually.")
        return await self._send_command(f"TOKEN {token_to_use}")

    def get_stored_token(self):
        return self.auth_token

    # ---------------------- Lifecycle ----------------------

    def close(self):
        if self.writer:
            self.writer.close()
            try:
                asyncio.ensure_future(self.writer.wait_closed())
            except AttributeError:
                pass  # Python <3.7 fallback


