define (require, exports, module)->
  Basic = require("coreDir/basic")
  class Frame extends Basic
    constructor:(ops)->
      super(ops)
      el = @
#      console.log(ops)
#      console.log(el)
      TZ.frameBox.push(el)
      return el
    rDefault:
      gridX: 0
      gridY: 0
      len:1
    len:""
    gridX: 0
    gridY: 0
    isInputing: false
    direction:"H"

  module.exports = Frame
  return module.exports