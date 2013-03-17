/**
 * show和create要分开？
  * @type {*}
 */
Tianzi.Frame = Tianzi.Component.extend({
    frameId : 0,
    status :{
        startGridX : 0,
        startGridY : 0,
        length : 0,
        direction : 'H'
    },
    rDefaults:{
        // 黄色方案
        fill : 'none',
        stroke : '#d31',
        x : 0,
        y : 0
    },
    contents :{}, //包含的square
    create : function(options){
        this.rElmt = paper.rect().attr(this.rDefaults);
        this.rElmt.TZBindObj = this;
//        console.log(this);
        var gridX = options.gridX ? options.gridX : 1,
            gridY = options.gridY ? options.gridY : 1;

        var len = options.length ? options.length : 1;
        var dire = options.direction ? options.direction : 'H'; //todo 需要一种改变status而且没有影响原型风险的方法
        this.status = {startGridX:gridX,startGridY:gridY,length:len};




        this.show();// FOR TEST  一开始应该不显示的
        frameBox.push(this);
    },
    show : function(){
        var pos = convertGridPosToSvg({gridX:this.status.gridX,gridY:this.status.gridY});
        var sideLen = tianzi.boardOption.gridWidth * tianzi.scale;
        if(this.status.direction && this.status.direction=='V'){
            this.rElmt.attr({width:sideLen ,height:sideLen*len,x:pos.x,y:pos.y});
//            console.log('vertical');
        }else{
            //默认状况是横着的
            this.rElmt.attr({width:sideLen * this.status.length ,height:sideLen,x:pos.x,y:pos.y});
//            console.log('horizonal');
        }
    }
})