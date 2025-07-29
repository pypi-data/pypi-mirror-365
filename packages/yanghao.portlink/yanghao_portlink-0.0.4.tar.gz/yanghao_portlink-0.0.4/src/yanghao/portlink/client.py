import asyncio
import websockets
import json

class PortLinkClient:
    def __init__(self, server_uri=None, debug=False, ping_timeout=60):
        # 默认使用公共服务器地址
        self.server_uri = server_uri if server_uri else "ws://106.75.139.203:8080/ws"
        self.websocket = None
        self.tunnel_addr = None
        self.debug = debug
        self.ping_timeout = ping_timeout
    
    def _debug_print(self, message):
        """Print debug information
        
        Args:
            message (str): Debug message
        """
        if self.debug:
            print(f"[DEBUG] {message}")

    async def __aenter__(self):
        self._debug_print(f"Connecting to server: {self.server_uri}")
        # 使用实例的ping_timeout参数，避免keepalive ping timeout错误
        self._debug_print(f"Using ping_timeout: {self.ping_timeout} seconds")
        self.websocket = await websockets.connect(self.server_uri, ping_timeout=self.ping_timeout)
        self._debug_print("WebSocket connection established")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            self._debug_print("Closing WebSocket connection")
            await self.websocket.close()
            self._debug_print("WebSocket connection closed")

    def get_tunnel_url(self):
        """Get tunnel URL
        
        Returns:
            str: Tunnel URL, returns None if not established
        """
        return self.tunnel_addr
    
    def print_tunnel_info(self):
        """Print tunnel information"""
        if self.tunnel_addr:
            print(f"\n=== PortLink Tunnel Information ===")
            print(f"Tunnel address: {self.tunnel_addr}")
            print(f"Status: Ready")
            print(f"================================\n")
        else:
            print("Tunnel not yet established")

    async def link(self, local_port):
        if not self.websocket:
            raise ConnectionError("Client not connected. Use 'async with' statement.")

        self._debug_print(f"Starting tunnel creation for local port {local_port}")
        
        self._debug_print("Waiting for server control message...")
        message = await self.websocket.recv()
        self._debug_print(f"Received message: {message}")
        
        try:
            control_msg = json.loads(message)
            self._debug_print(f"Parsed control message: {control_msg}")
            # Check message type and status
            if control_msg.get("type") == "control" and control_msg.get("status") == "ready":
                self.tunnel_addr = control_msg.get('addr')
                print(f"< Tunnel ready at {self.tunnel_addr}")
                self._debug_print(f"Tunnel address set: {self.tunnel_addr}")
                self.print_tunnel_info()
            else:
                print(f"< Unexpected control message: {message}")
                self._debug_print("Received unexpected control message, exiting")
                return
        except json.JSONDecodeError:
            print(f"< Unexpected message: {message}")
            self._debug_print("JSON parsing failed, exiting")
            return

        self._debug_print("Waiting for connection confirmation message...")
        message = await self.websocket.recv()
        self._debug_print(f"Received connection confirmation message: {message}")
        
        try:
            control_msg = json.loads(message)
            self._debug_print(f"Parsed connection confirmation message: {control_msg}")
            # Check message type and status
            if control_msg.get("type") != "control" or control_msg.get("status") != "connected":
                print(f"< Unexpected control message: {message}")
                self._debug_print("Received unexpected connection confirmation message, exiting")
                return
        except json.JSONDecodeError:
            print(f"< Unexpected message: {message}")
            self._debug_print("Connection confirmation message JSON parsing failed, exiting")
            return
        
        print("< Public connection established, connecting to local service.")
        self._debug_print(f"Public connection established, connecting to local service 127.0.0.1:{local_port}")
        
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', local_port)
            self._debug_print(f"Successfully connected to local service 127.0.0.1:{local_port}")
        except ConnectionRefusedError:
            print(f"> Error: Connection to localhost:{local_port} refused. Is the service running?")
            self._debug_print(f"Failed to connect to local service: 127.0.0.1:{local_port}")
            return

        print(f"> Connected to local service at localhost:{local_port}")
        self._debug_print("Starting local connection data transfer handling")

        await self._handle_local_connection(reader, writer)

    async def _handle_local_connection(self, reader, writer):
        self._debug_print("Creating data transfer tasks")
        ws_reader_task = asyncio.create_task(self._receive_from_ws(writer))
        local_reader_task = asyncio.create_task(self._send_to_ws(reader))
        heartbeat_task = asyncio.create_task(self._send_heartbeat())
        self._debug_print("All tasks created, starting data transfer")

        try:
            # Use ALL_COMPLETED instead of FIRST_COMPLETED to maintain long connection
            await asyncio.gather(
                ws_reader_task,
                local_reader_task,
                heartbeat_task
            )
        except asyncio.CancelledError:
            self._debug_print("Tasks cancelled")
            pass
        except Exception as e:
            print(f"Connection error: {e}")
            self._debug_print(f"Connection error details: {e}")
        finally:
            self._debug_print("Starting connection resource cleanup")
            # Cancel all tasks
            for task in [ws_reader_task, local_reader_task, heartbeat_task]:
                if not task.done():
                    task.cancel()
                    self._debug_print(f"Cancelling task: {task.get_name() if hasattr(task, 'get_name') else 'unknown'}")
            
            writer.close()
            await writer.wait_closed()
            self._debug_print("Local connection closed")
            print("Connection closed.")
            
    async def _send_heartbeat(self):
        """Send heartbeat messages periodically"""
        self._debug_print("Heartbeat task started")
        try:
            while True:
                # Send heartbeat every 30 seconds
                self._debug_print("Waiting 30 seconds before sending heartbeat")
                await asyncio.sleep(30)
                heartbeat_msg = json.dumps({"type": "heartbeat", "status": "ping"})
                await self.websocket.send(heartbeat_msg)
                print("Sent heartbeat")
                self._debug_print(f"Heartbeat message sent: {heartbeat_msg}")
        except asyncio.CancelledError:
            self._debug_print("Heartbeat task cancelled")
            pass
        except Exception as e:
            print(f"Heartbeat error: {e}")
            self._debug_print(f"Heartbeat error details: {e}")

    async def _receive_from_ws(self, writer):
        self._debug_print("Starting to receive data from WebSocket")
        try:
            async for message in self.websocket:
                # Handle heartbeat response message
                if isinstance(message, str):
                    self._debug_print(f"Received string message: {message}")
                    try:
                        msg = json.loads(message)
                        if msg.get("type") == "heartbeat" and msg.get("status") == "ok":
                            print("Received heartbeat response")
                            self._debug_print("Received heartbeat response")
                            continue
                    except json.JSONDecodeError:
                        self._debug_print("String message JSON parsing failed")
                        pass
                
                # Handle binary data
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
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PortLink Client - Simple TCP Tunnel Tool')
    parser.add_argument('local_port', type=int, help='Local service port')
    parser.add_argument('-s', '--server', type=str, help='Server address (e.g.: ws://example.com:8080/ws)')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode to show detailed information')
    parser.add_argument('-t', '--ping-timeout', type=int, default=60, help='WebSocket ping timeout in seconds (default: 60)')
    args = parser.parse_args()
    
    retries = 0
    retry_delay = 5  # Default 5 seconds reconnection delay
    
    while True:
        try:
            async with PortLinkClient(server_uri=args.server, debug=args.debug, ping_timeout=args.ping_timeout) as client:
                print(f"Connecting to server: {args.server if args.server else client.server_uri}")
                if args.debug:
                    print("[DEBUG] Debug mode enabled")
                    print(f"[DEBUG] Using ping_timeout: {args.ping_timeout} seconds")
                await client.link(args.local_port)
                # If exiting normally, no need to reconnect
                print("Task completed, normal exit.")
                break
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            retries += 1
            print(f"Connection error: {e}, trying to reconnect in {retry_delay} seconds (Attempt: {retries})")
            await asyncio.sleep(retry_delay)
        except KeyboardInterrupt:
            print("\nUser interrupted, program exiting.")
            break

if __name__ == "__main__":
    asyncio.run(main())