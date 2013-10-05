define("tianzi_game_main"
  [
    "coreDir/basic"
    "coreDir/board"
    "coreDir/text"
    "coreDir/frame"
    "coreDir/square"
    "coreDir/debug"
    "coreDir/util"
  ]
  (require,exports,module)->

    Basic = require("coreDir/basic");
    Board = require("coreDir/board");
    Text = require("coreDir/text");
    Square = require("coreDir/square");
    Frame = require("coreDir/frame");
    Util = require("coreDir/util");
    Debug = require("coreDir/debug");

    #todo refresh() in DebugCtrl affect the getTime()?  still don't know the $scope



    #angular
    #ngTianziMain = angular.module("tianziMain",[]);
    #  ngTianziMain.config()




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

    $("#ng-app").trigger("game_ready");

    exports.basic = Basic
    exports.board = Board
    #console.log(exports)

    return module.exports
)

