#UP - a convention based mini microservice management system

##Features
- Detect changes to applications and launch/re-launch automatically
- Provide a router, allowing services to talk using 'firstname'
- Common logging service, capturing stdout and write to timestamped log files 

##Why
- Because I wanted to run my Rasperry Pi applications as small apps using REST.
- Fun to see what it would take to have a lite weight, kubernetes inspired process management system running.

##How to use
- Put node.js or python apps in a directory and name them service_<name>.[js|py]
- Apps can have an optional prefix like pi_ or win_ if different implementations in different environments
- Start up by: up.sh <dirname> <port> <env>
- Logs will be written to <dirname>/up-logs/<name>.log.
  - up.log is the up master
  - up_route.log logs for the router
  - up.sh.log is log for the startup shell script and will hold log for up.py if it crash
  - Simple log filtering is available by setting LOG_LEVEL in up.py, default is INFO 
  - and messages starting with DEBUG will not be written by default.

##The up core apps:

|Application|Description|
|-----------|-----------|
| up.py | The up master application|
| up_route.js| The router, if no service named static is found then a page with list of services is shown at / |
| up.sh | The launch script |
| up-log.sh | Logger for the launch script|

##Example directory



