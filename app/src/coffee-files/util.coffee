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
        )
        if(data.matrix)
          tianzi.board.matrix = data.matrix
        if(data.Riddles)
          Util.initRiddles(data.Riddles)
        @
      # add frames
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
              sqr = new Square({gridX:gridX+i,gridY:gridY,txt:" "})

            else
              sqr = new Square({gridX:gridX,gridY:gridY + i, txt: " "})
        )

      saveGameData:()->
        sqrs = {}
        localStorage['Squares'] = null;
    #    console.log(TZ.squareBox);
        try
          _.each(TZ.squareBox,(item,idx)->
            # what happen to frames?
            sqrs[idx] ={ x : item.gridX , y : item.gridY, t: item.txt  }
          )
          localStorage.setItem('Squares',JSON.stringify(sqrs))
          #localStorage.setItem('Matrix',JSON.stringify(tianzi.board.matrix))
        catch e
          console.log(e.message)
          return false
        console.log("Game data saved in local storage")

      loadGameData: ()->
        Util.resetGame();
        squares = JSON.parse( localStorage.getItem('Squares'))
        sqrs_new_array = []
        _.each(squares,(obj,idx)->
          temp = {}
          temp.gridX = obj.x
          temp.gridY = obj.y
          temp.txt = obj.t
          sqrs_new_array.push(temp)
        )
        #matrix = JSON.parse( localStorage.getItem('Matrix'))
        Util.rebuildGame({Squares:sqrs_new_array})
        console.log("Load game data and rebuild")


      resetGame:()->
        _.each(TZ.squareBox,(item)->
          item.destroy()
        )
        TZ.squareBox = []
        TZ.board.refresh();
        console.log("Reset the squares")

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