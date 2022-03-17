import datetime
import getopt
import glob
import hashlib
import os
import socket
from subprocess import PIPE, Popen
from threading import Thread

import requests
import sys
import time

ARG_PORT = '--port='
ARG_ROUTE_HOST = '--routerHost='
LOG_LEVEL = 'INFO'

if not os.path.exists("up-logs"):
    os.makedirs("up-logs")

my_log_file = open("up-logs/up.log", "a")


def log(log_file, name, statement):
    if isinstance(statement, bytes):
        line = str(statement, 'utf-8', 'ignore')
    else:
        line = str(statement)
    if line.startswith("DEBUG") and LOG_LEVEL != 'DEBUG':
        return
    log_file.write(str(datetime.datetime.now()) + " " + name + ' ' + line + "\n")
    log_file.flush()


def logger(pipe, name):
    log_file = open("up-logs/" + name + ".log", "a")
    line = pipe.readline()
    while len(line) > 0:
        log(log_file, name, line)
        line = pipe.readline()
    log_file.close()


def log_me(line):
    log(my_log_file, "up", line)


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    log_me("get_free_port: " + str(port))
    return port


class UpService:
    def __init__(self, file, route_host):
        self.file = file
        self.route_host = route_host
        self.hash = hash_for_file(file)
        self.port = 0
        split = file.split('.')
        self.type = split[len(split) - 1]
        name = file[max(file.rfind('/'), file.rfind('\\')) + 1:]
        if len(name.split('service_')) > 1:
            # log_me('--- FOUND service         ' + name)
            self.name = name.split('service_')[1][:-(len(self.type) + 1)]
        else:
            self.name = name[:-(len(self.type) + 1)]
        self.command = None
        self.process = None
        self.thread = None

    def __eq__(self, other):
        return self.hash == other.hash

    def set_port(self, port):
        self.port = port

    def get_command(self, new_port=False):
        if self.command is None or new_port:
            self.port = get_free_tcp_port()
            if self.type == 'js':
                self.command = ['node', self.file, ARG_PORT + str(self.port), ARG_ROUTE_HOST + self.route_host]
            elif self.type == 'py':
                self.command = ['/usr/bin/python3', '-u', self.file, ARG_PORT + str(self.port),
                                ARG_ROUTE_HOST + self.route_host]
            elif self.type == 'sh':
                self.command = ['bash', self.file, ARG_PORT + str(self.port), ARG_ROUTE_HOST + self.route_host]
        return self.command

    def get_name(self):
        return self.name

    def get_name_port_option(self):
        return self.name + '.port=' + str(self.port)

    def has_stopped(self):
        url = "http://127.0.0.1:" + str(self.port) + "/live"
        try:
            v = requests.get(url)
            log_me("DEBUG: Checking live " + self.name + ":" + url + ", status_code: " + str(v.status_code))
            if v.status_code < 500:
                return False
            log_me("Has_stopped " + self.name + ", port: " + str(self.port) + ", status_code: " + str(v.status_code))
        except Exception as e:
            log_me("Has stopped " + self.name + ":" + url + ", Exception: " + str(type(e)))
        return True

    def stop(self):
        log_me("--- STOPPING:     " + self.name + ", command: " + str(self.process.args))
        self.process.terminate()

    def start(self, new_port=False):
        command = self.get_command(new_port)
        log_me("--- STARTING:    " + self.name + ", command: " + str(command))
        #        log_me(os.path.abspath(os.getcwd()))
        self.process = Popen(command, stdout=PIPE, stderr=PIPE)
        self.thread = Thread(target=logger, args=(self.process.stdout, self.name))
        self.thread.daemon = True
        self.thread.start()

    def restart(self):
        if not self.has_stopped():
            self.stop()
            self.process.wait()
        self.hash = hash_for_file(self.file)
        self.start(True)


class UpRoute(UpService):
    def __init__(self, file, port, services):
        super().__init__(file, None)
        log_me("--- CREATING:    " + self.name + ", port: " + str(port))
        self.services = services
        self.port = int(port)

    def get_command(self, new_port=False):
        if self.type == 'js':
            self.command = ['node', self.file, ARG_PORT + str(self.port)]
            self.command.extend(self.services_args())
        return self.command

    def services_args(self):
        ret = []
        for service in self.services:
            ret.append('--service.' + service.get_name_port_option())
        return ret

    def restart(self, services):
        self.services = services
        super().restart()


def hash_for_file(filename):
    sha = hashlib.md5()
    with open(filename, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha.update(byte_block)
    return sha.hexdigest()[:8]


def scan_services(environment, route_host):
    ret = []
    for file in glob.glob(environment + '_service*'):
        ret.append(UpService(file, route_host))
    for file in glob.glob('service*'):
        ret.append(UpService(file, route_host))
    return ret


def scan_route(services, directory, port):
    for file in glob.glob('route*'):
        return UpRoute(file, port, services)


def handle_config_change(running_services, configured_services):
    change = False
    to_remove = []
    for running in running_services:
        if running not in configured_services:
            log_me("Stopping: " + running.get_name() + " Service changed or removed.")
            running.stop()
            to_remove.append(running)
            change = True

    for stopped in to_remove:
        log_me("Removing: " + stopped.get_name())
        running_services.remove(stopped)

    for configured in configured_services:
        if configured not in running_services:
            r_list = list(filter(lambda r: (r.get_name() == configured.get_name()), running_services))
            if len(r_list) == 1:
                running = r_list[0]
                log_me("Service has changed: " + running.get_name())
                running.restart()
            else:
                log_me("Service added: " + configured.get_name())
                configured.start(True)
                running_services.append(configured)
            change = True
    return change


def get_options():
    route_dir = './'
    route_port = 8100
    environment = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:", ["route_dir=", "route_port=", "environment="])
    except getopt.GetoptError:
        log_me('service-config.py --port=<port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            log_me('service-config.py --port=<port>')
            sys.exit()
        elif opt == '--route_dir':
            route_dir = arg
        elif opt == '--route_port':
            route_port = arg
        elif opt == '--environment':
            environment = arg
    log_me('Start with route_dir=' + route_dir + ', route_port=' + str(route_port))
    return route_dir, route_port, environment


log_me(' - - - UP starting - - -')
my_ip = socket.gethostbyname(socket.gethostname())
options = get_options()
route_host = 'http://' + my_ip + ':' + str(options[1])

services = scan_services(options[2], route_host)
route = UpRoute(options[0] + '/up_route.js', options[1], services)
for service in services:
    service.start()
route.start()

log_me("---------------- Start monitoring -----------------")
time.sleep(15)
while True:
    for service in services:
        if service.has_stopped():
            service.restart()
    if route.has_stopped():
        route.restart(services)

    if handle_config_change(services, scan_services(options[2], route_host)):
        log_me("Change detected, restarting route")
        time.sleep(3)
        route.restart(services)

    newServices = scan_services(options[2], route_host)
    for service in newServices:
        found = False
        for curr in services:
            if service.name == curr.name:
                found = True
        if not found:
            services.append(service)

    time.sleep(2)
