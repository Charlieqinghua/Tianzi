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
    Debug = require("coreDir/debug");






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



    exports.basic = Basic
    exports.board = Board
    #console.log(exports)


)

