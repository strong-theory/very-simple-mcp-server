import http.server
import socketserver
import urllib.request
import urllib.error


def portforward(local_port, webservice_url):

    class ProxyHandler(http.server.BaseHTTPRequestHandler):
        def do_all(self):
            try:
                # Monta a URL completa do webservice
                url = f"{webservice_url}{self.path}"

                print(f"Forwarding request to: {url}")
                
                # Coleta headers do request
                headers = {key: value for key, value in self.headers.items() if key.lower() != 'host'}
                           
                # Lê o corpo da requisição, se houver
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else None
                
                # Cria a requisição para o webservice
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers=headers,
                    method=self.command
                )

                print(f"Request method: {self.command}")
                print(f"Request: {req.get_full_url()}")

                print(f"Request headers: {headers}")
                
                # Faz a requisição ao webservice
                with urllib.request.urlopen(req) as response:
                    # Obtém o status e headers da resposta
                    status = response.getcode()
                    response_headers = dict(response.getheaders())
                    response_body = response.read()
                    
                    # Envia o status e headers de volta ao cliente
                    self.send_response(status)
                    for header, value in response_headers.items():
                        if header.lower() not in ('transfer-encoding', 'content-encoding'):
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # Envia o corpo da resposta
                    self.wfile.write(response_body)
                    
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                for header, value in e.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        
        # Suporta todos os métodos HTTP
        def do_GET(self): self.do_all()
        def do_POST(self): self.do_all()
        def do_PUT(self): self.do_all()
        def do_DELETE(self): self.do_all()
        def do_PATCH(self): self.do_all()
        def do_HEAD(self): self.do_all()
        def do_OPTIONS(self): self.do_all()

    # Configura o servidor
    server_address = ('', local_port)
    httpd = socketserver.TCPServer(server_address, ProxyHandler)
    
    print(f"Port forwarding localhost:{local_port} to {webservice_url}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

# Exemplo de uso
if __name__ == "__main__":
    LOCAL_PORT = 1082
    WEBSERVICE_URL = "https://md59k.wiremockapi.cloud"  # Substitua pela URL real do webservice
    portforward(LOCAL_PORT, WEBSERVICE_URL)

