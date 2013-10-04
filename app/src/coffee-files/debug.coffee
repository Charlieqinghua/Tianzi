define (require, exports, module)->
  Frame = require("coreDir/frame")
  Square = require("coreDir/square")
  class Debug
    constructor:()->
      window.debug = @
      true
    printObjInfo:()->
      if( document.getElementById("debugInput").value != ''  )
        console.log("debug what?")
#      window.debugList =
#        squareBox : squareBox
#        textBox : textBox

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
      @

    # ng controller
    DebugCtrl = ($scope, $routeParams, $http)->
      $scope.square_box = TZ.squareBox
      $scope.frame_box = TZ.frameBox
      $scope.title = "Box panel"

      $scope.refresh = ()->
        console.log("refresh")
        $scope.square_box = TZ.squareBox
        return $scope.title
      $scope.squareOrder= ()->
        console.log("order square")

    window.TZ.DebugCtrl = DebugCtrl

  debug = new Debug
  window.debug=debug

  module.exports = Debug
  return module.exports