define (require, exports, module)->
  Basic = require("coreDir/basic")
  #todo z-index?  should go under the square and texts
  class Frame extends Basic
    constructor:(ops)->
      super(ops)
      el = @
      tmp = _.defaults({},ops,@defalutArg)
      @map_style_func(tmp,true)
      TZ.frameBox.push(el)
      return el
    defalutArg:
      gridX: 0
      gridY: 0
      len:1
    rDefault:
#      fill: "#F84040"
      fill: "transparent"
      stroke: "#EE430C"
      class: "frame"
    frameScope: null
    len: 1
    gridX: 0
    gridY: 0
    isInputing: false
    direction:"H"
    squresInside:[]
    map_style_func:(obj,shouldApply=false)->
      mp = {}
      mp['x'] = obj["gridX"] * BOARD_SIZE.gridWidth
      mp['y'] = obj["gridY"] * BOARD_SIZE.gridWidth
      if obj["direction"] == "H"
        #console.log(mp)
        mp['width'] = obj["len"] * BOARD_SIZE.gridWidth
        mp['height'] = BOARD_SIZE.gridWidth
      else
        mp['height'] = obj["len"] * BOARD_SIZE.gridWidth
        mp['width'] = BOARD_SIZE.gridWidth

      if shouldApply
        _.extend(@rAttrs,mp)
      return mp
    bind_r_event:()->
      el=@
      @rEle.click(el.click)
    click:(e)->
      console.log(arguments)

  # here?
  if window.TZ.frameScope
    Frame.prototype.frameScope = window.TZ.frameScope
    console.log("frameScope exists")

  module.exports = Frame
  return module.exports