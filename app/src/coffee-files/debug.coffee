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


  DebugCtrl = ($scope, $routeParams, $http)->
    true



  window.DebugCtrl = DebugCtrl
  debug = new Debug
  module.exports = Debug