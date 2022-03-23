import sys
from time import localtime, strftime

from lib.bottle import route, run
from utilities import port


@route('/live')
def live():
    return "Date & time here"


@route('/')
def date_and_time():
    return str(strftime("%a, %d %b %Y %H:%M:%S", localtime()))


print('----------- ' + sys.argv[0] + " starting on port: " + str(port(sys.argv[0], 8210)))
run(host='localhost', port=port(sys.argv[0], 8210), debug=True)
