/**
 * show和create要分开？
  * @type {*}
 * @fun 构造函数必须要传入的参数 Object:{ startGridX : Number, startGridY : Number, length : Number, direction : String 'H' or 'V' }
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
        stroke : '#a31',
        'stroke-width':2,
        'stroke-linejoin' : 'miter',
        x : 0,
        y : 0
    },
    contents :[], //包含的square
    create : function(options){
        var el = this;
        this.rElmt = paper.rect().attr(el.rDefaults);
        this.rElmt.TZBindObj = this;
        var gridX = options.startGridX ? options.startGridX : 1,
            gridY = options.startGridY ? options.startGridY : 1;
        var len = options.length ? options.length : 1;

        var dire = options.direction ? options.direction : 'H'; //todo 需要一种改变status而且没有影响原型风险的方法
        this.status = {startGridX:gridX,startGridY:gridY,length:len,direction:dire};

        this.show();// FOR TEST  一开始应该不显示的
        frameBox.push(this);
    },
    show : function(){
        var pos = convertGridPosToSvg({gridX:this.status.startGridX,gridY:this.status.startGridY});
//        console.log(pos);
        var sideLen = tianzi.boardOption.gridWidth * tianzi.scale;
        if(this.status.direction && this.status.direction=='V'){
            this.rElmt.attr({width:sideLen ,height:sideLen* this.status.length,x:pos.x,y:pos.y});
//            console.log('vertical');
        }else{
            //默认状况是横着的
            this.rElmt.attr({width:sideLen * this.status.length ,height:sideLen,x:pos.x,y:pos.y});
//            console.log('horizonal');
        }
    }
})