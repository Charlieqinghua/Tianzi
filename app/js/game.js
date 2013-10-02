define(null,["zepto","angularjs","src/tianzi_main"],function(require,exports,module) {

    var A = require('angularjs');
    var U = require('underscore');
    var zepto = require("zepto");

    var Tianzi = require.async("tianzi_game_main");

  //  //angular
    var ngTianziMain = angular.module("tianziMain",[]);
    //  ngTianziMain.config()

    var BoardCtrl = function($scope, $routeParams){

      $scope.getTime = function(){
        return new Date().toString();
      }


    }

    window.TZ = {};
    // controllers

    window.TZ.BoardCtrl = BoardCtrl; //ugly hack...



    $(document).ready(function(){
      TZ.paper = Raphael('svgWrapper',800,600);
    })
});




