import sys

from lib.bottle import route, run
from utilities import port, router_host
import requests



@route('/live')
def live():
    return "Time flies"


@route('/')
def time():
    try:
        url = str(router_host(sys.argv[0]))+"/dateandtime"
        v = requests.get(url)
        if v.status_code < 500:
            return str(v.content, 'utf-8', 'ignore')[17:25]
    except Exception as e:
        print("Exception: " + str(e))
    return 'Oh noooo'


print('----------- ' + sys.argv[0] + " starting on port: " + str(port(sys.argv[0], 8210)))
print('----------- ' + sys.argv[0] + " router on adress: " + str(router_host(sys.argv[0])))

run(host='localhost', port=port(sys.argv[0], 8210), debug=True)
