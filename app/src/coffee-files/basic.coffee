define (require, exports, module)->
#  console.log("basic")
  class Basic
    constructor:(ops)->
      el = @
      @guid = @makeGuid()
      # can we not use underscore?
      if not _.isEmpty(@rDefault)
        attrs = _.defaults({},ops,@rDefault)
        _.each(attrs,(v,k)->
          if k of el.__proto__
            el[k] = v
        )
      return @
    makeGuid: (len=16)->
      nu = Math.random().toString()
      id = nu.slice(nu.length-len+1,-1)
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
  #todo remember to return module.exports if you want sea.js works correctly in coffee
  return module.exports