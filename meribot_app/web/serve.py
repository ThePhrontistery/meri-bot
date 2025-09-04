from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
import sys

PORT = 8221
HOST = 'localhost'

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    os.chdir('static')  # Serve files from the static directory
    server_address = (HOST, PORT)
    httpd = server_class(server_address, handler_class)
    
    print(f"Serving at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server")
    
    # Open the browser automatically
    webbrowser.open(f'http://{HOST}:{PORT}/index.html')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == '__main__':
    run()
