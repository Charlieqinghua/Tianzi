define(null,
  [
    "coreDir/square"
    "coreDir/frame"
  ]
  (require,exports,module)->
    Square = require("coreDir/square");
    Frame = require("coreDir/frame");
    Util =
      rebuildGame: (data)->
        squares = data.Squares
        _.each(squares,(item)->
          sqr = new Square(item)
        )
        if(data.matrix)
          tianzi.board.matrix = data.matrix
        if(data.Riddles)
          Util.initRiddles(data.Riddles)
        @
      # add frames
      initRiddles:(riddles)->
        _.each(riddles,(item)->
          gridX = parseInt(item.gridX)
          len = parseInt(item.len)
          gridY = parseInt(item.gridY)
          dire = item.dir
          rdl = new Frame({gridX:gridX , gridY:gridY , len:len , direction:dire})
          rdl.draw()
          for i in [0,len]

            if(dire=='H')
              sqr = new Square({gridX:gridX+i,gridY:gridY,txt:" "})

            else
              sqr = new Square({gridX:gridX,gridY:gridY + i, txt: " "})
        )

      saveGameData:()->
        sqrs = {}
        localStorage['Squares'] = null;
    #    console.log(TZ.squareBox);
        try
          _.each(TZ.squareBox,(item,idx)->
            # what happen to frames?
            sqrs[idx] ={ x : item.gridX , y : item.gridY, t: item.txt  }
          )
          localStorage.setItem('Squares',JSON.stringify(sqrs))
          #localStorage.setItem('Matrix',JSON.stringify(tianzi.board.matrix))
        catch e
          console.log(e.message)
          return false
        console.log("Game data saved in local storage")

      loadGameData: ()->
        Util.resetGame();
        squares = JSON.parse( localStorage.getItem('Squares'))
        sqrs_new_array = []
        _.each(squares,(obj,idx)->
          temp = {}
          temp.gridX = obj.x
          temp.gridY = obj.y
          temp.txt = obj.t
          sqrs_new_array.push(temp)
        )
        #matrix = JSON.parse( localStorage.getItem('Matrix'))
        Util.rebuildGame({Squares:sqrs_new_array})
        console.log("Load game data and rebuild")


      resetGame:()->
        _.each(TZ.squareBox,(item)->
          item.destroy()
        )
        TZ.squareBox = []
        TZ.board.refresh();
        console.log("Reset the squares")

      scaleGame:()->
        new_scale = parseFloat($("#scaleInput").val())
        OPS.scale = new_scale

      convert_board_to_model:(cord,mode)->
        tmp_cord = {}
        switch mode
          when 'layer'
            tmp_cord.gridX = cord.x * TZ.scale / BOARD_SIZE.gridWidth >> 0
            tmp_cord.gridY = cord.y * TZ.scale / BOARD_SIZE.gridWidth >> 0
          when "SVG"
            tmp_cord.gridX = cord.x * TZ.scale / BOARD_SIZE.gridWidth - TZ.OPS.board_offset.x >> 0
            tmp_cord.gridY = cord.y * TZ.scale / BOARD_SIZE.gridWidth - TZ.OPS.board_offset.y >> 0
        #console.log(tmp_cord)
        return tmp_cord
#      convert_svg_board_arg:(obj,mode)->
#        tmp_cord = {}
#        switch mode
#          when "layer"
#            tmp_cord
#        true
      find_nearest_square:(obj,offsetMode="SVG")->
        tmp_cord=obj
        grid_offset = {x:0,y:0}
        if offsetMode=="SVG"
          tmp_cord.x += TZ.OPS.board_offset.x
          tmp_cord.y += TZ.OPS.board_offset.y

        gWid =  TZ.BOARD_SIZE.gridWidth
        # dx and dy are recording to the left top point
        dx = tmp_cord.x % gWid
        dy = tmp_cord.y % gWid
        grid_offset.x = if dx/gWid > 0.5 then 1 else 0
        grid_offset.y = if dy/gWid > 0.5 then 1 else 0
        tmp_cord = Util.convert_board_to_model({x:obj.x,y:obj.y},"SVG")
        console.log(@)
        console.log(tmp_cord)
        return {gridX:tmp_cord.x + grid_offset.x, gridY:tmp_cord.y + grid_offset.y}


      get_obj_by_id:(guid)->
        collection = _.union(TZ.squareBox,TZ.frameBox)

    window.Util = Util
    # ----- end of Util


    #extending Raphael
#    console.log("extending R")
#    window.Raphael.fn.addClass=(ele,className)->
#      old=ele.attr("class")
#      old_arr = old.split(" ")
#      console.log(old_arr)
#      if not _.some(old_arr,className)
#        ele.attr("class",old+" #{className}")
#
#    window.Raphael.fn.removeClass=(ele,className)->
#      old=ele.attr("class")
#      console.log(old)
#      reg =  new RegExp("\s#{className}\s")
#      new_str = old.replace(reg,"")
#      console.log(new_str)
#      ele.attr("class",new_str)

    module.exports = Util
)