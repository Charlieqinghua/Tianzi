define (require, exports, module)->
  console.log("basic")
  class Basic
    constructor:()->
      true
    id: 0
  module.exports = Basic
  true