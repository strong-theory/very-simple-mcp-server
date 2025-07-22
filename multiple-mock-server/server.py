import asyncio
import urllib.request
import urllib.error
import http.client
from email.parser import BytesParser
from io import BytesIO

async def portforward(local_port, webservice_url):
    async def handle_client(reader, writer):
        try:
            # Read the HTTP request
            request_data = await reader.read(4096)  # Read up to 4KB of data
            if not request_data:
                writer.close()
                return

            # Parse the HTTP request
            request_line, *header_lines = request_data.split(b'\r\n')
            method, path, _ = request_line.decode().split(' ', 2)
            
            # Parse headers
            headers = BytesParser().parsebytes(b'\r\n'.join(header_lines))
            content_length = int(headers.get('Content-Length', 0))
            
            # Read body if present
            body = await reader.read(content_length) if content_length > 0 else None

            # Build the full URL for the webservice
            url = f"{webservice_url}{path}"

            print(f"Forwarding request to: {url}")
            print(f"Request method: {method}")
            print(f"Request headers: {dict(headers)}")

            # Prepare headers, excluding 'host'
            request_headers = {key: value for key, value in headers.items() if key.lower() != 'host'}

            # Make the request to the webservice
            req = urllib.request.Request(
                url,
                data=body,
                headers=request_headers,
                method=method
            )

            try:
                with urllib.request.urlopen(req) as response:
                    status = response.getcode()
                    response_headers = dict(response.getheaders())
                    response_body = response.read()

                    # Prepare response headers, excluding problematic ones
                    response_headers = {
                        key: value for key, value in response_headers.items()
                        if key.lower() not in ('transfer-encoding', 'content-encoding')
                    }

                    # Build HTTP response
                    response_lines = [f"HTTP/1.1 {status} {http.client.responses.get(status, 'Unknown')}".encode()]
                    for header, value in response_headers.items():
                        response_lines.append(f"{header}: {value}".encode())
                    response_lines.append(b'\r\n')
                    response_lines.append(response_body)

                    # Send response to client
                    writer.write(b'\r\n'.join(response_lines))
                    await writer.drain()

            except urllib.error.HTTPError as e:
                # Handle HTTP errors
                response_lines = [f"HTTP/1.1 {e.code} {http.client.responses.get(e.code, 'Unknown')}".encode()]
                for header, value in e.headers.items():
                    response_lines.append(f"{header}: {value}".encode())
                response_lines.append(b'\r\n')
                response_lines.append(e.read())
                writer.write(b'\r\n'.join(response_lines))
                await writer.drain()

            except Exception as e:
                # Handle other errors
                writer.write(f"HTTP/1.1 500 Internal Server Error\r\n\r\nError: {str(e)}".encode())
                await writer.drain()

        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    # Start an async TCP server
    server = await asyncio.start_server(handle_client, 'localhost', local_port)
    print(f"Port forwarding localhost:{local_port} to {webservice_url}")

    # Keep the server running indefinitely
    async with server:
        await server.serve_forever()

async def main():
    LOCAL_PORT = 1080
    WEBSERVICE_URL = "https://md59k.wiremockapi.cloud"

    # Create a list of tasks for running servers in parallel
    tasks = []
    for i in range(5):
        port = LOCAL_PORT + i
        task = asyncio.create_task(portforward(port, WEBSERVICE_URL))
        tasks.append(task)

    # Wait for all tasks indefinitely
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down servers...")