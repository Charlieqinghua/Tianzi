define (require, exports, module)->
  Basic = require("coreDir/basic")
#  kk = new Basic()
#  console.log(Basic)
#  console.log(kk)
  class Square extends Basic
    constructor:(ops,shouldDraw=true)->
      super(ops)
      el = @
      tmp = _.defaults({},ops,@defalutArg)
      @map_style_func(tmp,true)
      if shouldDraw
        @draw()
      TZ.squareBox.push(el)

      return el
    defalutArg:
      gridX: 0
      gridY: 0
      txt:""
    rDefault:
      fill : "#f1f587",
      stroke : '#febe28',
      width : BOARD_SIZE.gridWidth,
      height :BOARD_SIZE.gridWidth,
      class: "square"
    txt:""
    gridX: 0
    gridY: 0
    isInputing: false
    rEle: null
    rText: null
    rBundle: null
    squareScope: null # for angular
    addText:(text)->
      @txt = text
    draw: ()->
      el=@
      if @rBundle
        #todo can we not add listenner to all the elements, but to the root element
        # and use event capture.   A way to optimize the performance
        @bind_event()
      else
        if not @rEle
          Util.convert_board_to_model()
          @rEle = @rPaper.rect().attr(@rAttrs)
        picks =[tx,ty,wid,hei] = _.values( _.pick(@rEle.attrs,["x","y","width","height"]) )
        x = tx+(wid/2)
        y = ty+(hei/2)
        @rText = @rPaper.text(x,y,@txt).attr({"font-size":OPS.text_size,"font-family":"verdana",fill:OPS.text_fill})
        @rBundle = @rPaper.set().push(el.rEle).push(el.rText)
        @bind_event()
    map_style_func:(obj,shouldApply=false)->
      mp = {}
      _.each(obj,(v,k)->
        switch(k)
          when 'gridX'
            return mp['x'] = v * BOARD_SIZE.gridWidth
          when 'gridY'
            return mp['y'] = v * BOARD_SIZE.gridWidth

          else
            return mp[k] = v

      )
      if shouldApply
        _.extend(@rAttrs,mp)

      return mp

    bind_event:()->
      el = @
      @rBundle.click (e)->
        el.click(e)
      @rEle.drag(el.drag)

    refresh:(ops)->
      #or should I use a events hub?
      el = @
      _.each(ops,(v,k)->
        if k of el
          el[k] = v
      )
      if @txt
        @rText.attr({text:el.txt})
      #todo   do we need this? or just use angular?
      sc = @squareScope
#      console.log(sc)
#      if sc
#        sc.$emit("test")

       # or should we just refresh this little part?
      sc.$digest()
#      sc.$on("refresh",()->
#
#      )
    destroy:()->
      # GC is a big problem
      @rEle.remove()
      @rText.remove()
      @rBundle.remove()
      @rBundle.remove()
    ## events
    click:(e)->
#      console.log(@)
#      console.log(e)
      target = e.target
      switch target.localNaame
        when "rect"
          #on the square
          true
        when "tspan"
          # on text
          true
      inputter = TZ.inputter # should not use zepto to select again , cause that will lose ["related-square"]
      TZ.inputWrapper.css({"left":e.pageX + "px","top":e.pageY + "px"}).show()

#      inputter.data("related-square",@).focus() # zepto is differnt frome jquery in .data(), zepto get things on the table
      inputter["related-square"] = @
      inputter.focus().val(@txt)

    drag:()->
      #todo if drag distance is less than a threadshold , treat it as a click
      console.log(arguments)
  module.exports = Square
  return module.exports