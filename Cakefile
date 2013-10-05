fs            = require 'fs'
path          = require 'path'
# todo how to find modules globally ?
# CoffeeScript  = require 'coffee-script'
# {spawn, exec} = require 'child_process'
# helpers       = require 'coffee-script/helpers'


# Built file header.
header = """
/**
*   Hikerpig's little demo named Tianzi
*/
"""



docco = (args,cb) ->
  files = fs.readdirSync 'app/src'
  the_files = ('src/' + file for file in files when file.match(/\.(lit)?coffee$/))
  run ['docco', '-o', ''].concat(the_files), cb

# Run a CoffeeScript through our node/coffee interpreter.
run = (args, cb) ->
  proc =         spawn 'node', ['bin/coffee'].concat(args)
  proc.stderr.on 'data', (buffer) -> console.log buffer.toString()
  proc.on        'exit', (status) ->
    process.exit(1) if status != 0
    cb() if typeof cb is 'function'

# Log a message with a color.
log = (message, color, explanation) ->
  console.log color + message + reset + ' ' + (explanation or '')


task "docco", docco 