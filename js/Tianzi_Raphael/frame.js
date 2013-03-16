Tianzi.Component = Class.extend({
    //todo 让大家都继承这个类，实现基本的调试功能  使用John 的简单继承法
    init : function(){
        var el = this;
    },
    debug : function(list){
        _.each(list,function(item,index){
            console.log(el[item.toString()]);//巨诡异的实现法，脑子被门夹了吧我！！
        })
    }
});
Tianzi.Component.prototype = {


}
Tianzi.Frame =function(options){
    this.create(options);
    return this;

}
Tianzi.Frame.prototype = {
    frameId : 0,
    rElmt : null,
    status :{
        startGridX : 0,
        startGridY : 0,
        length : 0
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
        var pos = convertGridPosToSvg({gridX:gridX,gridY:gridY});
        var len = options.length ? options.length : 1;
        this.status = {startGridX:gridX,startGridY:gridY,length:len};
        var sideLen = tianzi.boardOption.gridWidth * tianzi.scale;


        if(options.direction && options.direction=='vertical'){
            this.rElmt.attr({width:sideLen ,height:sideLen*len,x:pos.x,y:pos.y});
//            console.log('vertical');
        }else{
            //默认状况是横着的
            this.rElmt.attr({width:sideLen * len ,height:sideLen,x:pos.x,y:pos.y});
//            console.log('horizonal');
        }

        frameBox.push(this);
    }
}