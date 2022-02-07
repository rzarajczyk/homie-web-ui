import inspect
import json
import logging
import mimetypes
import os
import urllib.parse as urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer


def start_server(port, get_actions: dict, post_actions: dict) -> HTTPServer:
    logger = logging.getLogger('web')

    class ValidationException(Exception):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            logger.debug("Accepted HTTP request %s" % self.path)
            try:
                path, params = self.__parse(self.path)
                print(path)
                if path in get_actions:
                    output = self.__call_action(get_actions[path], params)
                    self.__respond(200, output)
                else:
                    return self.__media(path)
            except ValidationException as e:
                self.__respond(400, {'exception': "URL parse exception: %s" % str(e)})
                logger.error("ValidationException", e)
            except Exception as e:
                self.__respond(500, {'exception': str(e)})
                logger.error("Exception", e)

        def do_POST(self):
            logger.debug("Accepted HTTP request %s" % self.path)
            try:
                path, params = self.__parse(self.path)
                if path not in post_actions:
                    raise ValidationException("Unknown action POST %s" % path)
                output = self.__call_action(post_actions[path], params)
                self.__respond(200, output)
            except ValidationException as e:
                self.__respond(400, "URL parse exception: %s" % str(e))
                logger.error("ValidationException", e)
            except Exception as e:
                self.__respond(500, str(e))
                logger.error("Exception", e)

        def __media(self, path):
            path = './src/web/' + path
            if os.path.isfile(path):
                mime, encoding = mimetypes.guess_type(path)
                with open(path, 'rb') as file:
                    data = file.read()
                logger.info('Media: sending file %s as %s' % (path, mime))
                self.send_response(200)
                self.send_header('Content-type', mime)
                self.end_headers()
                self.wfile.write(data)
            else:
                logger.info('Media: file %s not found, sending 404' % (path))
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps('404: File Not Found', indent=4, default=lambda o: o.__dict__).encode('utf-8'))

        def __respond(self, code, output):
            logger.debug("Returning HTTP %s\n%s" % (code, output))
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(output, indent=4, default=lambda o: o.__dict__).encode('utf-8'))

        @staticmethod
        def __parse(url):
            try:
                url_parsed = urlparse.urlparse(url)
                url_params = urlparse.parse_qs(url_parsed.query)
                url_path = url_parsed.path
                return url_path, url_params
            except Exception as e:
                raise ValidationException(e)

        @staticmethod
        def __call_action(action, params):
            spec = inspect.getfullargspec(action)
            arg_count = len(spec.args)
            if arg_count == 0:
                result = action()
            elif arg_count == 1:
                result = action(params)
            else:
                raise Exception('Unable to call action: %s' % inspect.signature(action))
            return result if result is not None else {'status': 'ok'}

    get_endpoints = '\n'.join([' - GET %s' % endpoint for endpoint in get_actions.keys()])
    post_endpoints = '\n'.join([' - POST %s' % endpoint for endpoint in post_actions.keys()])
    logger.info('Will expose GET endpoints:\n%s' % get_endpoints)
    logger.info('Will expose POST endpoints:\n%s' % post_endpoints)
    logger.info('Starting httpserver on port %s' % port)

    return HTTPServer(('', port), RequestHandler)
