from distutils.log import debug
from json import dumps, loads, JSONEncoder, JSONDecoder
from flask_restful import Resource, Api

import socket
import time
import threading

from queue import Queue
from flask import Flask, request


socket.setdefaulttimeout(0.25)
print_lock = threading.Lock()

app = Flask(__name__)
api = Api(app)


@app.route("/scanports", methods=['POST'])
def ports():
    return {"start": "startPort"}


open_ports1 = []
open_ports2 = []


class PortScannerSlow(Resource):
    def get(self, networkAddress, startPort, endPort):

        netAdd = str(networkAddress)
        startPort = int(startPort)
        endPort = int(endPort)

        for port in range(startPort, endPort + 1):

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.connect((netAdd, port))
                    open_ports1.append(
                        {"networkAddress": netAdd, "startPort": startPort, "endPort": endPort, "openPort": port})
            except:
                pass

        return {"openPort": open_ports1}


class PortScannerFast(Resource):
    def get(self, networkAddress, startPort, endPort):

        startPort = int(startPort)
        endPort = int(endPort)
        target = str(networkAddress)
        t_IP = socket.gethostbyname(target)
        print('Starting scan on host: ', t_IP)

        t_IP = socket.gethostbyname(target)

        def portscan(port):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                con = s.connect((t_IP, port))
                with print_lock:
                    print(port, 'is open')
                    open_ports2.append(
                        {"networkAddress": target, "startPort": startPort, "endPort": endPort, "openPort": port})
                con.close()
            except:
                pass

        def threader():
            while True:
                worker = q.get()
                portscan(worker)
                q.task_done()

        q = Queue()
        startTime = time.time()

        for x in range(100):
            t = threading.Thread(target=threader)
            t.daemon = True
            t.start()

        for worker in range(startPort, endPort):
            q.put(worker)

        q.join()
        timeVar = time.time() - startTime

        return {"openPort": open_ports2, "time": timeVar}


api.add_resource(
    PortScannerSlow, '/portScannerSlow/<networkAddress>/<startPort>/<endPort>')

api.add_resource(
    PortScannerFast, '/portScannerFast/<networkAddress>/<startPort>/<endPort>')

if __name__ == "__main__":
    app.run(debug=True)
