const http = require('http');
const nodeStatic = require('node-static');
const yargs = require('yargs');

const arg = yargs
    .option('port', {
        alias: 'p',
        description: 'Port for starting server',
        type: 'integer',
        default: 8080,
    })
    .help()
    .alias('help', 'h')
    .argv;

const fileServer = new nodeStatic.Server('./public');

var myArgs = process.argv.slice(2);
console.log('myArgs: ', myArgs);

http.createServer(function (req, res) {
    if (req.url.split('/')[1] === 'live') {
        res.writeHead(200, {'Content-Type': 'text/plain'})
        res.end('Hello World!\n')
    } else {
        req.addListener('end', function () {
            fileServer.serve(req, res)
        }).resume()
    }
}).listen(arg.port)
