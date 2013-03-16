define(function(require, exports, module){
    var $ = require('zepto');
    var Tianzi = require('Tianzi');
/**
 *  文字的框框
 * @param arguments
 * @return {*}
 */
Tianzi.Square = function (arguments){

    var square = this.create(arguments);
//        console.log(this.status);
//        console.log(squareBox[0].status);
    return square;
};
Tianzi.Square.prototype = {
    el : null,  //创建（create）的时候制定的自身引用
    squareId : 0,
    status : {
        gridX : null,
        gridY : null,
        invoked : false
    },
    rElmt : null,
    relatatedText : null,  //对应的Tianzi.Text
    _tzDefaults : {  // 对应tianzi游戏的默认
        gridX : 0,
        gridY : 0
    },
    rDefaults : {    //主要是为了给raphael用  以后外观和内在要分开
        fill : "#f1f587",
//            stroke : '#eee',
        stroke : '#41bea8',
        width : 40,
        height :40
    },
    create : function(options){
        el = this; //需要么？
        this.status = {}; //注意要初始化！！！！要不然后面改单项有屁用！
//            adjustByScale();  //TODO  是基于proto的继承呢？ 还是每个类单独写一个
        applyDefaultPara.call(this.rDefaults,Tianzi.Square,this,options);
        this.rElmt = paper.rect().attr(this.rDefaults);  //按照外观的默认值构建   先用raphael的rect 以后可能会改成一个单独绘图函数
        var gX = options.gridX ? options.gridX : this._tzDefaults.gridX,
            gY = options.gridY ? options.gridY : this._tzDefaults.gridY;
//            console.log(this.status);
        this.status.gridX = gX;
        this.status.gridY = gY;
        /*console.log(options);
         console.log(gX);
         console.log(gY);*/
        this.rElmt.attr({x:gX * Tianzi.scale * this.rDefaults.width, y:gY * Tianzi.scale * this.rDefaults.height });
        //todo 和Tianzi.scale 相关的应该还有别的东西 最好整理下
        this.rElmt.TZBindObj = this;
        this.squareId = _.last(squareBox) ? _.last(squareBox).squareId + 1 : 1 ;
        squareBox.push(this);

        this.rElmt.click(function(event){
            this.TZBindObj.click({eventArg:event});  //这里的this指向的是Raphael??
        });
        this.rElmt.mouseover(function(event){
            this.stop().animateQueue(squareMouseoverQueue);
            this.toFront(); //放到最上层
            if (this.TZBindObj.relatedText) {
                console.log('eee');
                this.TZBindObj.relatedText.rElmt.toFront();
            } //文字要更上层
            this.TZBindObj.mouseover();
        });
        this.rElmt.mouseout(function(event){
            this.stop().animate({transform:'s1r0'},500);
        });
//            console.log('sqr created');

    },
    delete : function(){
        //寻找squareBox里id和自己相同的
//            squareBox
        if (this.relatedText) {
            var rt = this.relatedText;
            this.relatedText.rElmt.remove();
            _.reject(textBox,function(obj,key){ return  obj.textId == rt.textId;      }) //从textBox里移除
            this.relatedText.relatedSquare = null;
            this.relatedText = null; //这样就能销毁了么？
        }
        _.reject(squareBox,function(obj,key){ return  obj.squareId == this.squareId;      }) //从squareBox里移除
        //todo 如何destroy掉一个对象? 系统自动清除的前提是该对象没有被引用，那我怎么知道？
        this.rElmt.remove();
//            console.log(squareBox);

    },
    changeAppearence : function(options){
//            _.map(options,function(){  暂时不用每条都检查
//            console.log(options);
        this.rElmt.attr(options);
//            })
    },
    addText : function(txt){

        if(this.relatedText == null){
            var bBox = this.rElmt.getBBox();  //为什么用了el只会显示最后一个建立的box的数值？   用this才可以正确  也许因为我写的el = this 不对
//                没有文字就新建
            var tempTB = new Tianzi.Text({bBox : bBox,txt : txt});
            this.relatedText = tempTB;
            tempTB.relatedSquare = this;

            tempTB.textId =  _.last(textBox) ? _.last(textBox).textId + 1 : 1;   //有没有不需要underscore的快速解决方法？
            console.log(this.relatedText);
            tempTB.rElmt.attr(tempTB.textStyle); //TODO 以后要不要扩展下，改成tempTB.textStyle.default
            textBox.push(tempTB);
        }
    },
    refreshText : function(newTxt){
        if(! this.relatedText){
            this.addText(newTxt);
            inputBox[0].value = this.relatedText.rElmt.attr('text');
        }
        else{
            this.relatedText.rElmt.attr({text : newTxt});
            inputBox[0].value = '';  //todo 要显示建议值么？
        }
//            console.log('word refreshed');
    },
    /**
     * 空的框被单击后    添加文字
     * 按着alt键 删除    TODO 鼠标外观怎么改变？
     *
     */
    click : function(args){
//            console.log(args);
        if(args.eventArg && args.eventArg.altKey == true){   //奇怪了为什么不是 args.eventArg.altKey  ???
            this.delete();
//                console.log('alt');
        }
        else{
            this.status.invoked = true;
            tianzi.invokedObj.square = this;
            inputBox[0].focus();
            inputWrapper.show().css({top: event.pageY + 10 ,left:event.pageX - 20});
            //TODO  需要添加text对象？
        }

    },
    mouseover : function(){
//            console.log('mouse in');
//            console.log(this.rElmt);

    },
    mouseout : function(){}


};
    module.exports = Tianzi.Square;
});
