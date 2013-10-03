define("tianzi_game_main"
  [
    "coreDir/basic"
    "coreDir/board"
    "coreDir/text"
    "coreDir/frame"
    "coreDir/square"
    "coreDir/debug"
  ]
  (require,exports,module)->

    Basic = require("coreDir/basic");
    Board = require("coreDir/board");
    Text = require("coreDir/text");
    Square = require("coreDir/square");
    Frame = require("coreDir/frame");
    Debug = require("coreDir/debug");

    #console.log(Square)

    Util =
      rebuildGame: (data)->
        squares = data.Squares
        _.each(squares,(item)->
          sqr = new Square(item)
        )
        if(data.matrix)
          tianzi.board.matrix = data.matrix
        if(data.Riddles)
          @initRiddles(data.Riddles)
        @
      initRiddles:(data)->
        riddles = data
        _.each(riddles,(item)->
          gridX = parseInt(item.gridX)
          len = parseInt(item.len)
          gridY = parseInt(item.gridY)
          dire = item.dir
          rdl = new Frame({gridX:gridX , gridY:gridY , len:len , direction:dire})
          for i in [0,len]
            if(dire=='H')
              sqr = new Square({gridX:gridX+i,gridY:gridY})
            else
              sqr = new Square({gridX:gridX,gridY:gridY + i})
        )
    window.Util = Util

    #angular
    #ngTianziMain = angular.module("tianziMain",[]);
    #  ngTianziMain.config()

    BoardCtrl = ($scope, $routeParams)->

      $scope.getTime = ()->
        return Date().toString()

    window.TZ.BoardCtrl = BoardCtrl #ugly hack...

    Basic.prototype.rPaper = TZ.paper
    board = new Board()

    board.create();

    # test the UI
    startList = {
      Squares : {
        1 : { gridX:4, gridY:6 }
        2 : { gridX:9, gridY:2,txt:'老' }
        3 : { gridX:4, gridY:8 }
        4 : { gridX:3, gridY:9 }
        5 : { gridX:7, gridY:3 }
      }
      Riddles : {
        1 : { gridX:6 , gridY:5 , len:4 , dir:'H',desc : '这个'}
        2 : { gridX:4 , gridY:3 , len:6, dir:'V',desc : 'dd个'}
        3 : { gridX:10 , gridY:9 , len:4 , dir:'V',desc : '这个'}
      }
    }
    Util.rebuildGame({Squares : startList.Squares ,Riddles:startList.Riddles})


    exports.basic = Basic
    exports.board = Board
    #console.log(exports)


)

