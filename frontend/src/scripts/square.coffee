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
        # can we not add listenner to all the elements, but to the root element
        # and use event capture.   A way to optimize the performance
        @bind_own_event()
      else
        if not @rEle
          Util.convert_board_to_model()
          @rEle = @rPaper.rect().attr(@rAttrs)
        picks =[tx,ty,wid,hei] = _.values( _.pick(@rEle.attrs,["x","y","width","height"]) )
        x = tx+(wid/2)
        y = ty+(hei/2)
        @rText = @rPaper.text(x,y,@txt).attr({"font-size":OPS.text_size,"font-family":"verdana",fill:OPS.text_fill})
        @rBundle = @rPaper.set().push(el.rEle).push(el.rText)
        @bind_own_event()
    map_style_func:(obj,shouldApply=false)->
      mp = {}
      #todo even with the offset ok?
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

    bind_own_event:()->
      el = @
      @rBundle.click (e)->
        el.click(e)

      d = el.drag_event
      @rEle.drag(d.onmove,d.onstart,d.onend,@,@,@)  # should bind the context of sqaure
      #todo maybe we should not add so many listeners... just pass the guid as argument will be ok


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
      el = @
      @rEle.remove()
      @rText.remove()
      @rBundle.remove()
      @rBundle.remove()
      box_ref = null
      _.find(TZ.squareBox,(item,idx)->
        if item.guid == el.guid
          box_ref = idx
          return
      )
      console.log(box_ref)
      delete TZ.squareBox[box_ref]
    ## events
    click:(e)->
#      console.log(e)
      target = e.target
      has_shift_key = e.shiftKey
      switch target.localName
        when "rect"
          #on the square
          if has_shift_key
            @destroy()
            TZ.squareBox= _.compact(TZ.squareBox)
        when "tspan"
          # on text
          if has_shift_key
            @rText.remove()
            @txt=""
          true
        else
          console.log("nothing")
      if has_shift_key then return
      inputter = TZ.inputter # should not use zepto to select again , cause that will lose ["related-square"]
      TZ.inputWrapper.css({"left":e.pageX + "px","top":e.pageY + "px"}).show()

#      inputter.data("related-square",@).focus() # zepto is differnt frome jquery in .data(), zepto get things on the table
      inputter["related-square"] = @
      inputter.focus().val(@txt)

    drag_event:{
      onmove:(dx,dy,curX,curY,e)->
        #todo if drag distance is less than a threadshold , treat it as a click
#        console.log(arguments)
#        console.log(e)
      onstart:(x,y,e)->
#        console.log(arguments)
#        console.log(e)
#        e.srcElement
      onend:(e)->
#        console.log(arguments)
#        console.log("on end")
        console.log(e)
#        e.toElement
        to_ele = e.toElement
        to_tar_ele = @rPaper.getElementsByPoint(e.layerX,e.layerY)
        #console.log(to_tar_ele)
#        grid_arg = Util.convert_svg_board_arg({x:e.layerX,y:e.layerY},"layer")
        grid_arg = Util.find_nearest_square({x:e.layerX,y:e.layerY},"layer")
        console.log(grid_arg)

        bd = TZ.board
        if not bd.matrix[grid_arg.gridX][grid_arg.gridY]
          sqr = new Square(grid_arg,true)
        # todo how to do the 碰撞检测 ?
    }
  module.exports = Square
  return module.exports