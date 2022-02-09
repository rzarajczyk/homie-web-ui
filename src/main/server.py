import json
import logging
import mimetypes
import os
import urllib.parse as urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer


class Response:
    def code(self):
        return 200

    def headers(self) -> dict:
        return {}

    def response_bytes(self):
        return ""


class ErrorResponse(Response):
    def __init__(self, code, message):
        self._code = code
        self._message = message

    def code(self):
        return self._code

    def headers(self) -> dict:
        return {'Content-type': 'application/json'}

    def response_bytes(self):
        return json.dumps({'error': self._message}, indent=4, default=lambda o: o.__dict__).encode('utf-8')


class RedirectResponse(Response):
    def __init__(self, location):
        self._location = location

    def code(self):
        return 301

    def headers(self) -> dict:
        return {'Location': self._location}


class JsonOkResponse(Response):
    def __init__(self, payload):
        self._payload = payload

    def headers(self) -> dict:
        return {'Content-type': 'application/json'}

    def response_bytes(self):
        return json.dumps(self._payload, indent=4, default=lambda o: o.__dict__).encode('utf-8')


class StaticResourceResponse(Response):
    def __init__(self, mime, data):
        self._mime = mime
        self._data = data

    def headers(self) -> dict:
        return {'Content-type': self._mime}

    def response_bytes(self):
        return self._data


class Action:
    def can_handle(self, method, path, params, payload):
        return False

    def handle(self, method, path, params, payload) -> Response:
        return None


class JsonGet(Action):
    def __init__(self, path, callable):
        self.path = path
        self.callable = callable

    def can_handle(self, method, path, params, payload):
        return method == 'GET' and path == self.path

    def handle(self, method, path, params, payload) -> Response:
        output = self.callable(params)
        return JsonOkResponse(output)


class JsonPost(Action):
    def __init__(self, path, callable):
        self.path = path
        self.callable = callable

    def can_handle(self, method, path, params, payload):
        return method == 'POST' and path == self.path

    def handle(self, method, path, params, payload) -> Response:
        output = self.callable(params, payload)
        return JsonOkResponse(output)


class Redirect(Action):
    def __init__(self, path_from, path_to):
        self.path_from = path_from
        self.path_to = path_to

    def can_handle(self, method, path, params, payload):
        return path == self.path_from

    def handle(self, method, path, params, payload) -> Response:
        return RedirectResponse(self.path_to)


class StaticResources(Action):
    def __init__(self, path_prefix, dir):
        self._path_prefix = path_prefix
        self._dir = dir

    def can_handle(self, method, path, params, payload):
        return method == 'GET' and path.startswith(self._path_prefix)

    def handle(self, method, path, params, payload) -> Response:
        optional_slash = '/' if not self._dir.endswith('/') and not path.startswith('/') else ''
        file = self._dir + optional_slash + path
        if os.path.isfile(file):
            mime, encoding = mimetypes.guess_type(file)
            with open(file, 'rb') as f:
                data = f.read()
            return StaticResourceResponse(mime, data)
        else:
            logging.getLogger('web').info("Static resource %s not found" % file)
            return ErrorResponse(404, "File not found: %s" % path)


def start_server(port, actions: list[Action]) -> HTTPServer:
    logger = logging.getLogger('web')

    class ValidationException(Exception):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            logger.debug("Accepted HTTP request %s" % self.path)
            try:
                path, params = self.__parse(self.path)
                for action in actions:
                    if action.can_handle('GET', path, params, {}):
                        output = action.handle('GET', path, params, {})
                        return self.__respond(output)
                return self.__respond(ErrorResponse(404, "File not found"))
            except ValidationException as e:
                self.__respond(ErrorResponse(400, "URL parse exception: %s" % str(e)))
                logger.error("ValidationException", e)
            except Exception as e:
                self.__respond(ErrorResponse(500, str(e)))
                logger.error("Exception", e)

        def do_POST(self):
            logger.debug("Accepted HTTP request %s" % self.path)
            try:
                path, params = self.__parse(self.path)
                content_length = int(self.headers['Content-Length'])
                payload = self.rfile.read(content_length)
                for action in actions:
                    if action.can_handle('POST', path, params, payload):
                        output = action.handle('POST', path, params, payload)
                        return self.__respond(output)
                return self.__respond(ErrorResponse(404, "File not found"))
            except ValidationException as e:
                self.__respond(ErrorResponse(400, "URL parse exception: %s" % str(e)))
                logger.error("ValidationException", e)
            except Exception as e:
                self.__respond(ErrorResponse(500, str(e)))
                logger.error("Exception", e)

        def __respond(self, output):
            code = output.code()
            headers = output.headers()
            payload = output.response_bytes()
            logger.debug("Returning HTTP %s %s with payload of %s bytes" % (code, headers, len(payload)))
            self.send_response(code)
            for header in headers:
                self.send_header(header, headers[header])
            self.end_headers()
            self.wfile.write(payload)

        @staticmethod
        def __parse(url):
            try:
                url_parsed = urlparse.urlparse(url)
                url_params = urlparse.parse_qs(url_parsed.query)
                url_path = url_parsed.path
                return url_path, url_params
            except Exception as e:
                raise ValidationException(e)

    logger.info('Starting httpserver on port %s' % port)

    return HTTPServer(('', port), RequestHandler)
