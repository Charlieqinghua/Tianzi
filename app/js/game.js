define(null,["zepto","angularjs","src/tianzi_main"],function(require,exports,module) {

  var A = require('angularjs');
  var zepto = require("zepto");

  var Tianzi = require.async("tianzi_game_main");

  //global settings
  window.TZ = {};
  BOARD_SIZE = {width : 600 , height : 600 , xGrids : 18 ,yGrids : 18, gridWidth : 40};
  TZ.squareBox = []
  TZ.frameBox = []
  OPS={

  }






  $(document).ready(function(){
    TZ.paper = Raphael('svgWrapper',800,600);
    $("#ng-app").attr("ng-app","")
    console.log("ready");
//    angular.bootstrap(document.documentElement)
  })

  $("body").on("game_ready",null,function(){
    //get angular to work after all the work that have been done above
//    $("#ng-app").attr("ng-app","")            //get angular to work after all the work that have been done above

  })
});




