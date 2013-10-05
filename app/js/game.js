define(null,["zepto","angularjs","src/tianzi_main"],function(require,exports,module) {

  var A = require('angularjs');
  var zepto = require("zepto");

  var Tianzi = require.async("tianzi_game_main");

  //global game settings
  window.TZ = {};

  _.extend(TZ,{
    squareBox: [],
    frameBox : [],
    inputter : null,
    scale : 1

  })

  var OPS={
    text_size:"20px",
    text_fill: "#B4493A",
    BOARD_SIZE: {width : 600 , height : 600 , xGrids : 18 ,yGrids : 18, gridWidth : 40}
  }
  TZ.OPS = OPS
  window.OPS = OPS
  window.BOARD_SIZE = OPS.BOARD_SIZE ;

  var CONST = {

  }
  window.CONST = CONST


  $(document).ready(function(){
    TZ.paper = Raphael('svgWrapper',800,600);
    $("#ng-app").attr("ng-app","myModule")
    console.log("ready");
//    angular.bootstrap(document.documentElement)
    TZ.inputWrapper = $("#inputWrapper")
    TZ.inputter = TZ.inputWrapper.find("input");
  })





  window.TZ.mymodule = angular.module("myModule",[]);

  $("body").on("game_ready",null,function(){
    //get angular to work after all the work that have been done above
//    $("#ng-app").attr("ng-app","")            //get angular to work after all the work that have been done above

  })
});




