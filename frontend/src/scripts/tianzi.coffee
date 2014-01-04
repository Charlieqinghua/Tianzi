seajs.config
  base: '/scripts'
  paths:
    elements: '/scripts/elements'
  alias:
    angular: '../bower_components/angular/angular'
    underscore: '../bower_components/underscore/underscore'
    raphael: '../bower_components/raphael/raphael'
    zepto: '../bower_components/zepto/zepto'

    basic: 'elements/basic'
    board: 'elements/board'
    debug: 'elements/debug'
    frame: 'elements/frame'
    square: 'elements/square'
    text: 'elements/text'
    util: 'elements/util'


# 全局常量
window.BOARD_SIZE=
  gridWidth: 20


seajs.use ['tianzi_main']
