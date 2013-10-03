define (require, exports, module)->
  Basic = require("coreDir/basic");
  class Frame extends Basic
    constructor:()->
      true
  module.exports = Frame
  true