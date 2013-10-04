define (require, exports, module)->
  Frame = require("coreDir/frame")
  Square = require("coreDir/square")
  Debug =
    printObjInfo:()->
      if( document.getElementById("debugInput").value != ''  )
        console.log("debug what?")

      if(args.spercific)
        _.each(args.spercific,(val,key)->
          console.log(val);
        )

      else
        _.each(debugList,(val,key)->
          console.log(key);
          console.log(val);
        )
    saveData: ()->
      true

  window.debug = Debug

  # ng controller
  DebugCtrl = ($scope, $routeParams, $http)->
    $s = $scope
    $scope.square_box = TZ.squareBox
    $scope.frame_box = TZ.frameBox
    $scope.title = "Box panel"
    window.debug.debugScope = $scope

    $scope.refresh = ()->
      console.log("refresh")
      # can't we just trigger a 'change' event?
      $scope.square_box = TZ.squareBox
      $scope.frame_box = TZ.frameBox

      @
    $scope.squareOrder= ()->
      ### how to get this work? ###
      console.log("order square")


  window.TZ.DebugCtrl = DebugCtrl



  module.exports = Debug
  return module.exports