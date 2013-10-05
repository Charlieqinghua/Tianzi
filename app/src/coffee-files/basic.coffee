define (require, exports, module)->
#  console.log("basic")
  class Basic
    constructor:(ops)->
      el = @
      @guid = @makeGuid()
      # can we not use underscore?
      if not _.isEmpty(@defalutArg)
        attrs = _.defaults({},ops,@defalutArg)
        _.each(attrs,(v,k)->
          if k of el.__proto__
            el[k] = v
        )
      if not _.isEmpty((@rDefault))
        @rAttrs = @rDefault
      return @
    makeGuid: (len=16)->
      nu = Math.random().toString()
      id = nu.slice(nu.length-len+1,-1)
      return id
    arg_rarg_map_func: ()->
      grid
    guid: 0
    offsetToSvg :{x:0,y:0}
    rDefault: {}
    rPaper: null
    rAttrs: null
    refresh:()->
      true
    draw: ()->
      if not @rEle
        @rEle = @rPaper.rect().attr(@rAttrs)
    ngCtrl: []
    ngModel: []

  module.exports = Basic
  #todo tips remember to return module.exports if you want sea.js works correctly in coffee
  return module.exports