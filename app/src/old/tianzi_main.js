define("tianzi_game_main",
  [
    "coreDir/basic",
    "coreDir/board",
    "coreDir/text",
    "coreDir/frame"
  ],
  function(require,exports,module) {
    var Basic = require("coreDir/basic");
    var Board = require("coreDir/board");
    var Text = require("coreDir/text");

    //debugger;
    //angular
    //var ngTianziMain = angular.module("tianziMain",[]);
    //  ngTianziMain.config()

    var BoardCtrl = function($scope, $routeParams){

      $scope.getTime = function(){
        return new Date().toString();
      }


    }
    window.TZ.BoardCtrl = BoardCtrl; //ugly hack...

    Basic.prototype.rPaper = TZ.paper;
    board = new Board()
    board.create();



    exports.basic = Basic
    exports.board = Board
    //console.log(exports)

  }
);

