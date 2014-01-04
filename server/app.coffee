mongoose = require 'mongoose'
mongoStore = require 'connect-mongodb'
express = require 'express'
app = express()

PORT = 3939
app.set 'title', 'Tianzi'


# Configurations
app.configure 'development', ()->
    app.set('db-uri', 'mongodb://localhost/nodepad-development')
  app.use(express.errorHandler({ dumpExceptions: true }))
  app.set 'view options',
      pretty: true

app.configure ()->
  app.set('views', __dirname + '/views')
  app.use(express.favicon())
  app.use(express.bodyParser())
  app.use(express.cookieParser())
  app.use(express.session({ store: mongoStore(app.set('db-uri')), secret: 'topsecret' }))
  app.use(express.logger({ format: '\x1b[1m:method\x1b[0m \x1b[33m:url\x1b[0m :response-time ms' })
    app.use(express.methodOverride())
    app.use(express.static(__dirname + '/frontend/dist'))
    app.set 'mailOptions',
      host: 'localhost',
      port: '25',
      from: 'nodepad@example.com'
  )

# Router
app.get '/', (req, res)->
  body = 'Hello World'
  res.setHeader('Content-Type', 'text/plain')
  res.setHeader('Content-Length', body.length)
  res.end(body)

app.get '/game', (req, res)->
  true

app.listen(3939)
console.log("Listening Tianzi at #{PORT}")
