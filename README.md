#UP - a convention based mini "microservice management system"

##Features
- Detect (changes to) applications and automatically launch/re-launch.
- Provide a router, allowing services to talk using 'firstname'.
- Common logging service, capturing stdout and write to timestamped log files. 

##Why
- Because I wanted to run my Rasperry Pi applications as small apps using REST.
- Fun to see what it would take to build a lite weight, kubernetes inspired process management system.

##How
- Put node.js or python apps in a directory and name them ``service_<name>.[js|py]``
- Apps can have an optional prefix like ``pi_`` or ``win_`` if different implementations in different environments
- Start up by: ``up.sh <dirname> <port> <env>``
- Logs will be written to ``<dirname>/up-logs/<name>.log``.
  - **up.log** is the up master
  - **up_route.log** for the router
  - **up.sh.log** is log for the startup shell script and will hold log for up.py if it crash
  - Simple log filtering is available by setting ``LOG_LEVEL`` in up.py, default is ``INFO`` 
  - Messages starting with DEBUG will not be written by default.
- The apps must
  - read the commandline properties:
    - ``--port=<port number>`` to listen on
    - ``--routerHost=<address to router>`` address to router, where other services can be contacted
  - answer on ``/live``


##The up core apps:

|Application|Description|
|-----------|-----------|
| up.py | The up master application|
| up_route.js| The router, if no service named ``static`` is found then a page with list of services is shown at / |
| up.sh | The launch script |
| up-log.sh | Logger for the launch script|

##Example directory
As name indicate hold a set of **up ready** services
- ``xx_service_static.js`` a server for static files in ``public`` directory
- ``public/index.html`` File showing date & time
- ``service_dateandtime.pl`` provide current date and time
- ``service_date.py`` use ``service_dateandtime.pl`` to provide date
- ``service_time.py`` use ``service_dateandtime.pl`` to provide time


