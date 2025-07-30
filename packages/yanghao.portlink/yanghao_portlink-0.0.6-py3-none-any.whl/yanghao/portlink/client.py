import asyncio
import websockets
import json
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PortLinkClient:
    def __init__(self, local_port, server_uri, debug=False):
        self.local_port = local_port
        self.server_uri = server_uri
        self.websocket = None
        self.ping_task = None
        self.debug = debug

    def _debug_print(self, msg):
        if self.debug:
            logging.debug(msg)

    def print_tunnel_info(self):
        print("--------------------------------------------------")
        print(f"  Tunnel established:")
        print(f"    Local service:  127.0.0.1:{self.local_port}")
        print(f"    Remote address: {self.remote_addr}")
        print("--------------------------------------------------")

    async def __aenter__(self):
        logging.info(f"Connecting to server: {self.server_uri}")
        try:
            self.websocket = await websockets.connect(
                self.server_uri,
                ping_interval=None,
                ping_timeout=None
            )
            logging.info("WebSocket connection established")
            self.ping_task = asyncio.create_task(self._send_pings())
            return self
        except Exception as e:
            logging.error(f"Failed to connect to server: {e}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.ping_task:
            self.ping_task.cancel()
        if self.websocket:
            await self.websocket.close()
            logging.info("WebSocket connection closed")

    async def send_control_message(self, msg):
        try:
            await self.websocket.send(json.dumps(msg))
            self._debug_print(f"[CONTROL] Sent: {msg}")
        except Exception as e:
            logging.error(f"Failed to send control message: {e}")

    async def _send_pings(self):
        while True:
            try:
                await asyncio.sleep(30)  # Send a ping every 30 seconds
                if self.debug:
                    logging.debug("Sending PING to server")
                await self.websocket.ping()
                if self.debug:
                    logging.debug("Sent PING to server")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error sending ping: {e}")
                break

    async def link(self, local_port):
        self.local_port = local_port
        self.local_connections = {}
        self.server_domain = self.server_uri.split('/')[2].split(':')[0]
        self._debug_print(f"Server domain set to: {self.server_domain}")

        try:
            while True:
                message = await self.websocket.recv()
                if isinstance(message, str):
                    await self._handle_control_message(message)
                elif isinstance(message, bytes):
                    await self._handle_data_message(message)

        except websockets.ConnectionClosed as e:
            logging.info(f"Connection closed: {e.code} {e.reason}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            for _reader, writer in self.local_connections.values():
                writer.close()
                await writer.wait_closed()
            logging.info("All local connections closed.")

    async def _handle_control_message(self, message):
        try:
            msg = json.loads(message)
            self._debug_print(f"[CONTROL] Received: {msg}")
    
            msg_type = msg.get("type")
            status = msg.get("status")
    
            if msg_type == "control":
                if status == "ready":
                    self.tunnel_addr = msg.get('addr')
                    if self.tunnel_addr and "localhost" in self.tunnel_addr:
                        port = self.tunnel_addr.split(":")[1]
                        self.remote_addr = f"{self.server_domain}:{port}"
                    else:
                        self.remote_addr = self.tunnel_addr
                    print(f"< Tunnel ready at {self.remote_addr}")
                    self.print_tunnel_info()
                elif status == "new_connection":
                    conn_id = msg.get("conn_id")
                    if conn_id:
                        logging.info(f"New connection request for conn_id: {conn_id}")
                        asyncio.create_task(self._handle_new_local_connection(conn_id))
                    else:
                        logging.warning("new_connection message received without conn_id")
                elif status == "connected":
                    logging.info(f"Connection confirmed for conn_id: {msg.get('conn_id')}")
                elif status == "error":
                    logging.error(f"Server error: {msg.get('error')} for conn_id: {msg.get('conn_id')}")
                else:
                    logging.warning(f"Unhandled control message status: {status}")
            else:
                logging.warning(f"Received non-control message: {msg}")
    
        except json.JSONDecodeError:
            logging.warning(f"Could not decode control message: {message}")

    async def _handle_data_message(self, message):
        try:
            # 解封装消息: [conn_id_len (1 byte)][conn_id][payload]
            conn_id_len = message[0]
            conn_id = message[1:1+conn_id_len].decode('utf-8')
            data = message[1+conn_id_len:]

            if conn_id in self.local_connections:
                _reader, writer = self.local_connections[conn_id]
                self._debug_print(f"Forwarding {len(data)} bytes from WS to local conn {conn_id}")
                writer.write(data)
                await writer.drain()
            else:
                logging.warning(f"Received data for unknown or closed conn_id: {conn_id}")
        except IndexError:
            logging.warning("Received malformed data message.")

    async def _handle_new_local_connection(self, conn_id):
        self._debug_print(f"Attempting to connect to 127.0.0.1:{self.local_port} for conn_id {conn_id}")
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', self.local_port)
            self.local_connections[conn_id] = (reader, writer)
            logging.info(f"New local connection for conn_id {conn_id} established.")
            # Send connected message to server
            await self.send_control_message({"type": "control", "status": "connected", "conn_id": conn_id})
            asyncio.create_task(self._forward_local_to_ws(conn_id, reader, writer))
        except ConnectionRefusedError:
            logging.error(f"Connection refused for conn_id {conn_id} to 127.0.0.1:{self.local_port}")
            # Optionally, notify the server that the connection failed
        except Exception as e:
            logging.error(f"Error creating new local connection {conn_id}: {e}")

    async def _forward_local_to_ws(self, conn_id, reader, writer):
        self._debug_print(f"Starting to forward data from local conn {conn_id} to WS")
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    self._debug_print(f"Local connection {conn_id} closed by peer.")
                    break
                
                conn_id_bytes = conn_id.encode('utf-8')
                conn_id_len = len(conn_id_bytes)
                message = bytes([conn_id_len]) + conn_id_bytes + data

                await self.websocket.send(message)
                self._debug_print(f"Forwarded {len(data)} bytes from local conn {conn_id} to WS")
        except (asyncio.CancelledError, ConnectionResetError):
            self._debug_print(f"Forwarding task for {conn_id} was cancelled or reset.")
        except Exception as e:
            logging.error(f"Error forwarding data for conn {conn_id}: {e}")
        finally:
            self._debug_print(f"Cleaning up connection {conn_id}")
            writer.close()
            await writer.wait_closed()
            # Optionally, notify server of connection closure
            asyncio.create_task(self.send_control_message({"type": "control", "status": "close_connection", "conn_id": conn_id}))
            self.local_connections.pop(conn_id, None)

    async def _receive_from_ws(self, writer):
        self._debug_print("Starting to receive data from WebSocket")
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    self._debug_print(f"Received binary data, length: {len(message)} bytes")
                    writer.write(message)
                    await writer.drain()
                    self._debug_print("Binary data forwarded to local service")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")
            self._debug_print(f"WebSocket connection closed details: {e}")
        except Exception as e:
            print(f"Error receiving from WebSocket: {e}")
            self._debug_print(f"Error receiving data from WebSocket details: {e}")
        finally:
            self._debug_print("WebSocket receive task ended, closing writer")
            writer.close()

    async def _send_to_ws(self, reader):
        self._debug_print("Starting to read data from local service and send to WebSocket")
        try:
            while True:
                self._debug_print("Waiting to read data from local service...")
                data = await reader.read(4096)
                if not data:
                    self._debug_print("Local service connection closed, stopping data transmission")
                    break
                self._debug_print(f"Read {len(data)} bytes from local service")
                await self.websocket.send(data)
                self._debug_print("Data sent to WebSocket")
        except asyncio.CancelledError:
            self._debug_print("Send to WebSocket task cancelled")
            pass
        except Exception as e:
            self._debug_print(f"Error sending data to WebSocket: {e}")

async def main():
    print("PortLink Client - Simple TCP Tunnel Tool")
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PortLink Client - Simple TCP Tunnel Tool')
    parser.add_argument('local_port', type=int, help='Local service port')
    parser.add_argument('-s', '--server', type=str, default='ws://106.75.139.203:8080/ws', help='Server address (e.g.: ws://example.com:8080/ws)')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode to show detailed information')
    parser.add_argument('-t', '--ping-timeout', type=int, default=61, help='WebSocket ping timeout in seconds (default: 61)')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled")
    
    retries = 0
    retry_delay = 5  # Default 5 seconds reconnection delay
    
    while True:
        try:
            async with PortLinkClient(local_port=args.local_port, server_uri=args.server, debug=args.debug) as client:
                logging.info(f"Connecting to server: {args.server if args.server else client.server_uri}")
                await client.link(args.local_port)
                logging.info("Task completed, normal exit.")
                break
        except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            retries += 1
            logging.error(f"Connection error: {e}, trying to reconnect in {retry_delay} seconds (Attempt: {retries})")
            await asyncio.sleep(retry_delay)
        except KeyboardInterrupt:
            logging.info("\nUser interrupted, program exiting.")
            break

if __name__ == "__main__":
    asyncio.run(main())