define (require, exports, module)->
  Basic = require("./basic")
  # todo don't need this
  class Text extends Basic
    constructor:()->
      true
  module.exports = Text
  true
