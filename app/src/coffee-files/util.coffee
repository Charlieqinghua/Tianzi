define(null,
  [
    "coreDir/square"
    "coreDir/frame"
  ]
  (require,exports,module)->
    Square = require("coreDir/square");
    Frame = require("coreDir/frame");
    Util =
      rebuildGame: (data)->
        squares = data.Squares
        _.each(squares,(item)->
          sqr = new Square(item)
          sqr.draw()
        )
        if(data.matrix)
          tianzi.board.matrix = data.matrix
        if(data.Riddles)
          Util.initRiddles(data.Riddles)
        @

      initRiddles:(riddles)->
        _.each(riddles,(item)->
          gridX = parseInt(item.gridX)
          len = parseInt(item.len)
          gridY = parseInt(item.gridY)
          dire = item.dir
          rdl = new Frame({gridX:gridX , gridY:gridY , len:len , direction:dire})
          rdl.draw()
          for i in [0,len]
            if(dire=='H')
              sqr = new Square({gridX:gridX+i,gridY:gridY})

            else
              sqr = new Square({gridX:gridX,gridY:gridY + i})
        )
      convert_board_to_model:(cord,mode)->
        tmp_cord = {}
        switch mode
          when 'layer'
            tmp_cord.gridX = cord.x * TZ.scale / BOARD_SIZE.gridWidth >> 0
            tmp_cord.gridY = cord.y * TZ.scale / BOARD_SIZE.gridWidth >> 0
        #console.log(tmp_cord)
        return tmp_cord
    window.Util = Util
    module.exports = Util
)