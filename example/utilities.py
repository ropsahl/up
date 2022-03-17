import getopt

import sys
import threading


def p_err(my_name, option):
    print('GetOptError: ' + my_name + option)


def port(my_name, default_port=8200):
    port = default_port
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:", ["port=","routerHost="])
    except getopt.GetoptError:
        p_err(my_name, ' --port=<port>')
    for opt, arg in opts:
        if opt == '-h':
            p_err(my_name, ' --port=<port>')
            sys.exit()
        elif opt in ("-p", "--port"):
            port = arg
    print("Starting on port:" + str(port))
    return port


def router_host(my_name):
    url = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:", ["port=","routerHost="])
    except getopt.GetoptError:
        p_err(my_name, ' --routerHost=<url>')
    for opt, arg in opts:
        if opt == '-h':
            p_err(my_name, ' --routerHost=<url>')
            sys.exit()
        elif opt == "--routerHost":
            url = arg
    print("Using router at:" + str(url))
    return url


# Function wrapper
def periodic_task(interval, times = -1):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap
