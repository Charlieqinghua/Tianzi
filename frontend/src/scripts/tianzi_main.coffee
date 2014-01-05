define([
  "elements/basic"
  "elements/board"
  "elements/text"
  "elements/frame"
  "elements/square"
  "elements/debug"
  "elements/util"
  "angular"
]
  ,(require,exports,module)->

    Basic = require("elements/basic")
    Board = require("elements/board")
    Text = require("elements/text")
    Square = require("elements/square")
    Frame = require("elements/frame")
    Util = require("elements/util")
    Debug = require("elements/debug")

    #todo refresh() in DebugCtrl affect the getTime()?  still don't know the $scope


    #angular
    #ngTianziMain = angular.module("tianziMain",[])
    #  ngTianziMain.config()

    A = require("angular")
    _ = zepto = require("zepto")
    Tianzi = require.async("tianzi_main")
    
    #global game settings
    window.TZ = {}
    _.extend TZ,
      squareBox: []
      frameBox: []
      inputter: null
      scale: 1

    window.OPS =
      text_size: "20px"
      text_fill: "#B4493A"
      BOARD_SIZE:
        width: 600
        height: 600
        xGrids: 18
        yGrids: 18
        gridWidth: 40

      board_offset: # board offset to svg tag
        x: 40
        y: 40

    window.TZ.OPS = OPS
    window.OPS = OPS
    window.BOARD_SIZE = OPS.BOARD_SIZE
    window.CONST = {}

    $(document).ready ->
      TZ.paper = Raphael("svgWrapper", 800, 600)
      $("#ng-app").attr "ng-app", "myModule"
      console.log "ready"
      
      #    angular.bootstrap(document.documentElement)
      TZ.inputWrapper = $("#inputWrapper")
      TZ.inputter = TZ.inputWrapper.find("input")

    window.TZ.mymodule = angular.module("myModule", [])

    $("body").on "game_ready", null, ->


    # ------ So Tianzi can start

    Basic.prototype.rPaper = TZ.paper
    board = new Board()

    board.create()
    # inputter events
    inputter = TZ.inputter
    inputter.on "focus", (e)->
      console.log("on focus")
      rs = inputter["related-square"]
      eve("square.editing",rs,rs)
    inputter.on "blur", (e)->
      console.log("blur")
      rs = inputter["related-square"]
      eve("square.leave_editing",rs,rs)

    inputter.on("keydown",(e)->
      # what if in mobile device?
      keycode = e.keyCode
      #console.log(keycode)
      switch keycode
        when 13
          $el = $(@)
          val = $el.val()

          rs = inputter["related-square"]
          try
            if(rs)
              rlt = rs.refresh({txt : val})
              TZ.inputWrapper.hide()
              inputter.val("")
          catch er
            console.log(er.message)

    )
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

    earchCompleteStop()
    

    exports.basic = Basic
    exports.board = Board
    #console.log(exports)

    return module.exports
)

