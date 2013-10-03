define (require,exports,module)->
  Basic = require("coreDir/basic");
  class Board extends Basic
    constructor:()->
      #@__proto__.constructor(arguments)

    rDefaults:
      # #蓝黄
      # fill:"#41bea8",
      # stroke:'none'

      # 黄色
      fill:'#febe28'
      stroke:'none'

    matrix : []

    refresh : (atbt,options)->
      #以后扩写时候可以甄别atbt

      @matrix = []


    create : ()->
      el = @
      @refresh()
      @rElmt = @rPaper.set()
      @rElmt.TZBindObj = this
      @rElmt.push(
          @rPaper.rect(@offsetToSvg.x,@offsetToSvg.y,BOARD_SIZE.xGrids * BOARD_SIZE.gridWidth,BOARD_SIZE.yGrids * BOARD_SIZE.gridWidth).attr(@rDefaults)
      )
#            绑定给raphael的click函数
#      @rElmt.click((event)->
#        console.log(event)
#        mouseToSvg =  offsetX:event.offsetX, offsetY:event.offsetY
##                console.log(mouseToSvg)
#        el.click(mouseToSvg : mouseToSvg ,eventArg : event)
#      )
#
#    click : (args)->
#      point = args.mouseToSvg
#
#      if args.eventArg.shiftKey == true
#        #console.log('shift')
#        svgPos = getPointInGrid(x:point.offsetX, y:point.offsetY)
#        #tempSqr=new Tianzi.Square(svgPos)

  module.exports = Board
