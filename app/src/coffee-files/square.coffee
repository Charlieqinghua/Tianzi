define (require, exports, module)->
  Basic = require("coreDir/basic")
#  kk = new Basic()
#  console.log(Basic)
#  console.log(kk)
  class Square extends Basic
    constructor:(ops)->
      super(ops)
      el = @
      @map_style_func(@defalutArg,true)
      TZ.squareBox.push(el)
      return el
    defalutArg:
      gridX: 0
      gridY: 0
      txt:""
    rDefault:
      fill : "#f1f587",
      stroke : '#febe28',
      width : BOARD_SIZE.gridWidth,
      height :BOARD_SIZE.gridWidth
    txt:""
    gridX: 0
    gridY: 0
    isInputing: false
    rEle: null
    rBundle: null
    squareScope: null # for angular
    addText:(text)->
      @txt = text
    refresh:()->
      #todo   do we need this? or just use angular?
      sc = @squareScope
      @squareScope.$digest()
      sc.$on("refresh",()->

      )
    draw: ()->
      if not @rEle
        @rEle = @rPaper.rect().attr(@rAttrs)
    map_style_func:(obj,shouldApply=false)->
      mp = {}
      _.each(obj,(v,k)->
        switch(k)
          when 'gridX'
            return mp['width'] = v * BOARD_SIZE.gridWidth
          when 'gridY'
            return mp['height'] = v * BOARD_SIZE.gridWidth

          else
            return mp[k] = v

      )
      #console.log(mp)
      if shouldApply
        _.extend(@rAttrs,mp)

      return mp


  module.exports = Square
  return module.exports