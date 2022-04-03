const http = require('http')
const httpProxy = require('http-proxy')
const yargs = require('yargs')
const argv = yargs
  .option('port', {
    alias: 'p',
    description: 'Port for the this server'
  })
  .option('service', {
    alias: 's',
    description: 'Services to serve. Example --service.config.port=453845 -s.static.port=765'
  })
  .help()
  .alias('help', 'h')
  .argv

function getService (name) {
  console.log('DEBUG getService: ' + name + ' hasOwnProperty:' + argv.hasOwnProperty(name))
  if (name && argv?.service?.hasOwnProperty(name)) {
    return argv.service[name]
  }
  return undefined
}

function getServiceLinks () {
  let ret = '<html><meta http-equiv="refresh" content="3" /><body><h1>Up manage the following services:</h1><ul>'
  if (argv.service && Object.keys(argv.service).length > 0) {
    for (let s in argv.service) {
      ret += '<li><a href="/' + s + '">' + s + '</a> <a href="/' + s + '/live">/live</a></li>'
    }
  } else {
    ret += 'No services running'
  }

  return ret + '</body></html>'
}

const proxy = httpProxy.createProxyServer({})

let ip = require('ip')
console.log('Running on ' + ip.address() + ':' + argv.port)

for (let s in argv.service) {
  console.log('Service:' + s)
}

http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token')

  console.log('DEBUG Request: ' + req.url)
  var url = req.url
  var serviceName = url.split('/')[1]
  var service = getService(serviceName)
  if (service === undefined) {
    service = getService('static')
  } else {
    req.url = url.substr(serviceName.length + 1)
  }

  req.addListener('end', function () {
    if (service === undefined) {
      res.write(getServiceLinks())
      res.end()
    } else {
      proxy.web(req, res, { target: 'http://localhost:' + service.port })
    }
  }).resume()
}).listen(argv.port)
