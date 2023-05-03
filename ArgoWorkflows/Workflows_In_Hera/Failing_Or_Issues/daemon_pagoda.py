# The following script can be launched in Hera 5.1.3 but the server
# is not run as deamon (which is reflected by the YAML Manifest given by AW
# UI). The server thus runs without ending and consumer is never triggered.

import sys, os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "PaGoDa_definition")
)
from pagoda_cluster_definition import define_cluster

define_cluster()


### The following is an adapted (to version > 531) copy of
# https://github.com/argoproj-labs/hera/blob/4.4.2/examples/daemon.py
"""Enablement of https://argoproj.github.io/argo-workflows/variables/
This example creates two tasks, one of the Tasks is a deamond task and its IP address is shared with the second task
The daemoned task operates as server, serving an example payload, with the second task operating as a client, making
http requests to the server."""

from hera.workflows import DAG, Env, script, Task, Workflow


@script()
def server():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class MyServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes("{'name':'John'}", "utf-8"))

    webServer = HTTPServer(("0.0.0.0", 8080), MyServer)
    webServer.serve_forever()


@script()
def consumer():
    import http.client
    import os

    print(os.environ)
    server_ip = os.environ["SERVER_IP"].replace('"', "")
    connection = http.client.HTTPConnection(f"{server_ip}:8080")
    connection.request("GET", "/")
    response = connection.getresponse()
    print(response.read())


with Workflow(generate_name="variables", entrypoint="entry") as w:
    with DAG(name="entry"):
        d = server(name="daemon", daemon=True)
        t = consumer(
            name="consumer",
            env=[Env(name="SERVER_IP", value=d.ip)],
        )
        d >> t

w.create()
