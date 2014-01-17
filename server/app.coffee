inspect = require('util').inspect
path = require 'path'
mongoose = require 'mongoose'
mongoStore = require 'connect-mongodb'
express = require 'express'
handlebars = require 'express3-handlebars'
#hbsmodule = require 'express-hbs'
ejs = require 'ejs'
app = express()

hbs = handlebars.create()
PORT = 3939
app.set 'title', 'Tianzi'


# Configurations
app.configure 'development', ()->
  app.set('db-uri', 'mongodb://localhost/nodepad-development')
  app.use(express.errorHandler({ dumpExceptions: true }))
  app.set 'view options',
    pretty: true

app.configure ()->
  #app.engine('handlebars', hbs.engine ) # handlebars 怎么都不行啊
  app.engine('hbs', hbs.engine ) # 靠... 原来是要这样使用app.engine  ..
  #app.set('view engine', 'handlebars')
  app.set('view engine', 'hbs')
  #app.engine('html', ejs.renderFile )
  #app.set('view engine', 'html')
  app.set('views', __dirname + '/views')
  app.use(express.favicon())
  app.use(express.bodyParser())
  app.use(express.cookieParser())
  app.use(express.session({ store: mongoStore(app.set('db-uri')), secret: 'topsecret' }))
  #app.use(express.logger({ format: '\x1b[1m:method\x1b[0m \x1b[33m:url\x1b[0m :response-time ms' })
  app.use(express.methodOverride())
  app.use(express.static( path.join( __dirname, '../', 'frontend/build')) )
  #console.log path.join( __dirname, '../', 'frontend/build')
  
# ------Router ----------
app.get '/', (req, res)->
  body = 'Hello World'
  res.setHeader('Content-Type', 'text/plain')
  res.setHeader('Content-Length', body.length)
  res.end(body)

# game
app.get '/game$', (req, res)->
  #console.log(hbs)
  #console.log app
  res.render path.join __dirname, '../frontend/build/index'
  #app.use express.static path.join( __dirname, '../', 'frontend/build')
  #res.redirect '/index.html'
  true

# 静态 ??
#app.use '/game', express.static path.join( __dirname, '../', 'frontend/build')

#app.get '/gametest', (req, res)->
  #res.render 'gametest' # wrong ?

app.listen(3939)
console.log("Listening Tianzi at #{PORT}")
