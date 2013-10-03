define (require, exports, module)->
  #console.log("basic")

  class Basic
    constructor:()->
      @guid = @makeGuid()
      @
    makeGuid: (len=16)->
      nu = Math.random().toString()
      id = nu.slice(nu.length - len,-1)
      return id
    guid: 0
    offsetToSvg :{x:0,y:0}
    rDefault: {}
    rPaper:{}
    refresh:()->
      true

    ngCtrl: []
    ngModel: []
  module.exports = Basic