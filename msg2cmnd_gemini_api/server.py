import json
from functools import cached_property
from http.server import BaseHTTPRequestHandler, HTTPServer

from msg2cmnd_gemini import get_cmnd


# This class is initialized every time the request is received.
class HTTPRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def post_data(self):
        """
        Gets request post data.
        """
        content_length = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(content_length).decode('utf-8'))

    def send_ok_response(self, data):
        """
        Send HTTP OK response with body.
        """
        self.send_response_only(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        serialized_data = json.dumps(data).encode('utf-8')
        self.wfile.write(serialized_data)

    def do_POST(self):
        """
        Handles POST requests.
        """
        try:
            message = self.post_data['message']
        except KeyError:
            self.send_error(400)
            return None

        command = get_cmnd(message)
        if command is None:
            self.send_error(400, 'Gemini failed! Use payed version!')
            return None

        self.send_ok_response(command)


def main():
    server = HTTPServer(('127.0.0.58', 8000), HTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
