define (require,exports,module)->
  class Board
    constructor:
      true

    rDefaults:
      # #蓝黄
      # fill:"#41bea8",
      # stroke:'none'

      # 黄色
      fill:'#febe28'
      stroke:'none'

    matrix : []
    offsetToSvg :{x:20,y:20}
    refresh : (atbt,options)->
      #以后扩写时候可以甄别atbt

      this.matrix = []


    create : ()->
      el = @
      this.refresh()
      this.rElmt = paper.set()
      this.rElmt.TZBindObj = this
      this.rElmt.push(
          paper.rect(this.offsetToSvg.x,this.offsetToSvg.y,BOARD_SIZE.xGrids * BOARD_SIZE.gridWidth,BOARD_SIZE.yGrids * BOARD_SIZE.gridWidth).attr(this.rDefaults)
      )
#            绑定给raphael的click函数
      this.rElmt.click((event)->
        console.log(event)
        mouseToSvg =  offsetX:event.offsetX, offsetY:event.offsetY
#                console.log(mouseToSvg)
        el.click(mouseToSvg : mouseToSvg ,eventArg : event)
      )

    click : (args)->
      point = args.mouseToSvg

      if args.eventArg.shiftKey == true
        #console.log('shift')
        svgPos = getPointInGrid(x:point.offsetX, y:point.offsetY)
        #tempSqr=new Tianzi.Square(svgPos)
