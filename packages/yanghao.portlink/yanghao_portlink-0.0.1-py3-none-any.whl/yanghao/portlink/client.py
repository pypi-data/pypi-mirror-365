import asyncio
import websockets
import json

class PortLinkClient:
    def __init__(self, server_uri=None):
        # 默认使用公共服务器地址
        self.server_uri = server_uri if server_uri else "ws://106.75.139.203:8080/ws"
        self.websocket = None
        self.tunnel_addr = None

    async def __aenter__(self):
        self.websocket = await websockets.connect(self.server_uri)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            await self.websocket.close()

    def get_tunnel_url(self):
        """获取隧道URL
        
        Returns:
            str: 隧道URL，如果未建立则返回None
        """
        return self.tunnel_addr
    
    def print_tunnel_info(self):
        """打印隧道信息"""
        if self.tunnel_addr:
            print(f"\n=== PortLink 隧道信息 ===")
            print(f"隧道地址: {self.tunnel_addr}")
            print(f"状态: 已就绪")
            print(f"=======================\n")
        else:
            print("隧道尚未建立")

    async def link(self, local_port):
        if not self.websocket:
            raise ConnectionError("Client not connected. Use 'async with' statement.")

        message = await self.websocket.recv()
        try:
            control_msg = json.loads(message)
            # 检查消息类型和状态
            if control_msg.get("type") == "control" and control_msg.get("status") == "ready":
                self.tunnel_addr = control_msg.get('addr')
                print(f"< Tunnel ready at {self.tunnel_addr}")
                self.print_tunnel_info()
            else:
                print(f"< Unexpected control message: {message}")
                return
        except json.JSONDecodeError:
            print(f"< Unexpected message: {message}")
            return

        message = await self.websocket.recv()
        try:
            control_msg = json.loads(message)
            # 检查消息类型和状态
            if control_msg.get("type") != "control" or control_msg.get("status") != "connected":
                print(f"< Unexpected control message: {message}")
                return
        except json.JSONDecodeError:
            print(f"< Unexpected message: {message}")
            return
        
        print("< Public connection established, connecting to local service.")
        
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', local_port)
        except ConnectionRefusedError:
            print(f"> Error: Connection to localhost:{local_port} refused. Is the service running?")
            return

        print(f"> Connected to local service at localhost:{local_port}")

        await self._handle_local_connection(reader, writer)

    async def _handle_local_connection(self, reader, writer):
        ws_reader_task = asyncio.create_task(self._receive_from_ws(writer))
        local_reader_task = asyncio.create_task(self._send_to_ws(reader))
        heartbeat_task = asyncio.create_task(self._send_heartbeat())

        try:
            # 使用ALL_COMPLETED而不是FIRST_COMPLETED，保持长连接
            await asyncio.gather(
                ws_reader_task,
                local_reader_task,
                heartbeat_task
            )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            # 取消所有任务
            for task in [ws_reader_task, local_reader_task, heartbeat_task]:
                if not task.done():
                    task.cancel()
            
            writer.close()
            await writer.wait_closed()
            print("Connection closed.")
            
    async def _send_heartbeat(self):
        """定期发送心跳消息"""
        try:
            while True:
                # 每30秒发送一次心跳
                await asyncio.sleep(30)
                heartbeat_msg = json.dumps({"type": "heartbeat", "status": "ping"})
                await self.websocket.send(heartbeat_msg)
                print("Sent heartbeat")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Heartbeat error: {e}")

    async def _receive_from_ws(self, writer):
        try:
            async for message in self.websocket:
                # 处理心跳响应消息
                if isinstance(message, str):
                    try:
                        msg = json.loads(message)
                        if msg.get("type") == "heartbeat" and msg.get("status") == "ok":
                            print("Received heartbeat response")
                            continue
                    except json.JSONDecodeError:
                        pass
                
                # 处理二进制数据
                if isinstance(message, bytes):
                    writer.write(message)
                    await writer.drain()
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")
        except Exception as e:
            print(f"Error receiving from WebSocket: {e}")
        finally:
            writer.close()

    async def _send_to_ws(self, reader):
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                await self.websocket.send(data)
        except asyncio.CancelledError:
            pass

async def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='PortLink 客户端 - 简单的 TCP 隧道工具')
    parser.add_argument('local_port', type=int, help='本地服务端口')
    parser.add_argument('-s', '--server', type=str, help='服务器地址 (例如: ws://example.com:8080/ws)')
    args = parser.parse_args()
    
    retries = 0
    retry_delay = 5  # 默认5秒重连延迟
    
    while True:
        try:
            async with PortLinkClient(server_uri=args.server) as client:
                print(f"连接到服务器: {args.server if args.server else client.server_uri}")
                await client.link(args.local_port)
                # 如果正常退出，不需要重连
                print("任务完成，正常退出。")
                break
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            retries += 1
            print(f"连接错误: {e}，{retry_delay}秒后尝试重连 (尝试次数: {retries})")
            await asyncio.sleep(retry_delay)
        except KeyboardInterrupt:
            print("\n用户中断，程序退出。")
            break

if __name__ == "__main__":
    asyncio.run(main())