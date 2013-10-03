define (require, exports, module)->
  Basic = require("coreDir/basic")
#  kk = new Basic()
#  console.log(Basic)
#  console.log(kk)
  class Square extends Basic
    constructor:(ops)->
      super(ops)
      el = @
#      attrs = _.defaults({},ops,@rDefault)
#      _.each(attrs,(v,k)->
#        if k of el.__proto__
#          el[k] = v
#      )
      TZ.squareBox.push(el)
      return el
    rDefault:
      gridX: 0
      gridY: 0
      txt:""
    txt:""
    gridX: 0
    gridY: 0
    isInputing: false
    addText:(text)->
      @txt = text
    refresh:()->
      #todo   do we need this? or just use angular?


  module.exports = Square
  return module.exports