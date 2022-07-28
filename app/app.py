#!/usr/bin/env python3

import logging
import os
import signal

import requests
import dateutil.parser as dp

from datetime import datetime
import json

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

DEFAULT_PORT = 5299
DEFAULT_TRACCAR_HOST = 'http://traccar:8082'

LOGGER = logging.getLogger(__name__)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself
        LOGGER.debug("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

        T2T.process_data(post_data)

    def do_GET(self):
        self.send_error(418, "I'm a teapot")


class TTN2Traccar():
    def __init__(self, conf: dict):
        # Initialize the class.
        super().__init__()

        self.port = conf.get("Port")
        self.traccar_host = conf.get("TraccarHost")

    def listen(self):
        server = ThreadingHTTPServer(('0.0.0.0', self.port), HTTPRequestHandler)
        LOGGER.info(f"Starting server at http://127.0.0.1:{self.port}")
        server.serve_forever()

    def read_testfile(self, filename):
        with open(filename) as f:
            self.process_data(f.read())

    
    def tx_to_traccar(self, query: str):
        # Send position report to Traccar server
        LOGGER.debug(f"tx_to_traccar({query})")
        url = f"{self.traccar_host}/?{query}"
        print(url)
        try:
            post = requests.post(url)
            # logging.debug(f"POST {post.status_code} {post.reason} - {post.content.decode()}")
            if post.status_code == 400:
                logging.warning(
                    f"{post.status_code}: {post.reason}. Please create device with matching identifier on Traccar server.")
                raise ValueError(400)
            elif post.status_code > 299:
                logging.error(f"{post.status_code} {post.reason} - {post.content.decode()}")
        except OSError:
            logging.exception(f"Error sending to {url}")


    def process_data(self, data):
        j = json.loads(data)
        # print(json.dumps(j, indent=2))

        um = j.get("uplink_message")
        decpayload = um.get("decoded_payload")
        
        if not decpayload:
            return

        lat = decpayload['latitude']
        lon = decpayload['longitude']

        if not (lat and lon):
            logging.debug("Lat or Lon not found")
            return

        dev_id = j.get("end_device_ids").get("device_id")
        timestamp = int(datetime.timestamp(dp.parse(um.get("settings").get("time"))))

        query_string = ""

        
        for attr in ['altitude', 'speed', 'course']:
            if attr in decpayload:
                #traccar needs bearing instead of course
                query_string += f"&{attr.replace('course','bearing')}={decpayload[attr]}"

        # extra attributes
        # for attr in ['from', 'to', 'via', 'symbol', 'symbol_table', 'comment']:
        #     if attr in decpayload:
        #         query_string += f"&APRS_{attr}={decpayload[attr]}"
                
        
        query_string = f"id={dev_id}&lat={lat}&lon={lon}&timestamp={timestamp}" + query_string
        try:
            self.tx_to_traccar(query_string)
        except ValueError:
            logging.warning(f"id={dev_id}")





if __name__ == '__main__':
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    logging.basicConfig(level=log_level)


    def sig_handler(sig_num, frame):
        logging.debug(f"Caught signal {sig_num}: {frame}")
        logging.info("Exiting program.")
        exit(0)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    
    config = {}
    config["Port"] = os.environ.get("PORT", DEFAULT_PORT)
    config["TraccarHost"] = os.environ.get("TRACCAR_HOST", DEFAULT_TRACCAR_HOST)

    T2T = TTN2Traccar(config)
    # T2T.read_testfile('SamplePost.json')
    T2T.listen()
    


