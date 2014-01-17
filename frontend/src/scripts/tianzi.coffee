seajs.config
  base: '/scripts'
  paths:
    elements: '/scripts/elements'
  alias:
    #angular: '../bower_components/angular/angular'
    #underscore: '../bower_components/underscore/underscore'
    #raphael: '../bower_components/raphael/raphael'
    #zepto: '../bower_components/zepto/zepto'

    angular: '../lib/angular'
    underscore: '../lib/underscore'
    raphael: '../lib/raphael'
    zepto: '../lib/zepto'


    basic: 'elements/basic'
    board: 'elements/board'
    debug: 'elements/debug'
    frame: 'elements/frame'
    square: 'elements/square'
    text: 'elements/text'
    util: 'elements/util'


#seajs.use ['zepto', 'Raphael'], ()->
define 'tianzi', ['zepto', 'raphael', 'angular'], (require, exports, module)->
  A = require("angular")
  _ = require 'zepto'
  #Raphael = window.Raphael

  # get angular to work after all the work that have been done above
  $("#ng-app").attr("ng-app","")


  # 全局常量
  #global game settings
  window.TZ = {}

  TZ =
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
    debugger
    #console.log 'Raphael', Raphael
    #TZ.paper = Raphael("svgWrapper", 800, 600)
    $("#ng-app").attr "ng-app", "myModule"
    console.log "ready"
    
    TZ.inputWrapper = $("#inputWrapper")
    TZ.inputter = TZ.inputWrapper.find("input")

  window.TZ.mymodule = angular.module("myModule", [])



  #$("body").on "game_ready", null, ->

    #    angular.bootstrap(document.documentElement)

  console.log arguments


  console.log 'tianzi main before'
  require ['tianzi_main'], ()->
    console.log 'tianzi main before'
    require 'tianzi_main'


# load this
seajs.use 'tianzi'
