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
  return argv.service[name]
}

function getServiceLinks () {
  let ret = '<html><body><h1>Router with following services</h1><ul>'
  for (let s in argv.service) {
    ret += '<li><a href="/' + s + '/live">' + s + '/live</a></li>'
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
