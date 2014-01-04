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

    guid: 0
    offsetToSvg :{x:0,y:0}
    rDefault: {}
    rPaper: null
    rAttrs: null

    makeGuid: (len=16)->
      nu = Math.random().toString()
      id = nu.slice(nu.length-len+1,-1)
      return id
    arg_rarg_map_func: ()->
      true

    refresh:()->
      true
    draw: ()->
      if not @rEle
        @rEle = @rPaper.rect().attr(@rAttrs)
        @bind_r_event()
      @rAttrs = @rEle.attr()

    bind_r_event:()->
      # should call this method after the Element is created
      true
    ngCtrl: []
    ngModel: []
    addClass: (className)->
      old=@rEle.attr("class")
      old_arr = old.split(" ")
      console.log(old_arr)
      if not _.some(old_arr,className)
        @rEle.attr("class",old+" #{className}")

    removeClass: (className)->
      old=@rEle.rAttrsattr("class")
      console.log(old)
      reg =  new RegExp("\s#{className}\s")
      new_str = old.replace(reg,"")
      console.log(new_str)
      @rEle.attr("class",new_str)
  module.exports = Basic
  #todo tips remember to return module.exports if you want sea.js works correctly in coffee
  return module.exports