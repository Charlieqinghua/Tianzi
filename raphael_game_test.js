//逻辑和绘图应该分开   绘图先使用raphael  以后可以考虑canvas

//如果整个board大小在运行中改变（skew），default参数要随之改变么？
var paper;

$(document).ready(function(){
    var mouseToSvg;
    var svgWrapper = document.getElementById('svgWrapper');
    paper = Raphael('svgWrapper',800,600);
    Tianzi(paper);
})


Tianzi = function(paper) {
//    var squareBox = [];
//    相关的大参数
    var BOARD_SIZE = {width : 600 , height : 600};


//    调试方便的外露部分，暂时的     以后要封装进Tianzi的闭合作用域
    window.squareBox = [];
    window.TianZi = this;
    var R = paper;
//    this.debug = function(){
//        R = paper;
//    }
    /**
     *  放字框的游戏板子
     * @param {Object} 传递的 Raphael 实体
     * @return {*}
     */
    Tianzi.Board = function() {
        this.create();
        return this;
    };
    Tianzi.Board.prototype = {
        rElmt : null,
        fillColor : "#dddd44",
        refresh : function(){},
        create : function(){
            var el = this;
            this.rElmt = paper.set();
            this.rElmt.TZBindObj = this;
            this.rElmt.push(
                paper.rect(0,0,BOARD_SIZE.width,BOARD_SIZE.height).attr({fill:"#dddd44","fill-opacity": 0.5})
            );
//            绑定给raphael的click函数
            this.rElmt.click(function(event){
                mouseToSvg = { offsetX:event.offsetX, offsetY:event.offsetY };
                el.click(mouseToSvg);
            })
        },
        click : function(point){
//            console.log('board click');

//            没想好封装名
            if(true){
                var tempSqr = new Tianzi.Square({x:point.offsetX,y:point.offsetY});
//                console.log(tempSqr.el);

                tempSqr.changeAppearence({
                    x : point.offsetX - point.offsetX % tempSqr.rDefaults.width,
                    y : point.offsetY - point.offsetY % tempSqr.rDefaults.height}
                );  // tempSqr.rDefaults这个写法麻烦， 考虑以后要不要把及时的参数放到Square.status 里面……
                squareBox.push(tempSqr);
            }

        }
    };
    /**
     *  文字的框框
     * @param arguments
     * @return {*}
     */
    Tianzi.Square = function (arguments){

        var square = this.create(arguments);

        return square;
    };
    Tianzi.Square.prototype = {
        el : null,  //创建（create）的时候制定的自身引用
        id : 0,
        status : {
            cx : 0,
            cy : 0
        },
        rElmt : null,
        relatatedText : null,
        rDefaults : {    //主要是为了给raphael用  以后外观和内在要分开
            fill : "#a4d",
            width : 50,
            height :50,
            x : 50,
            y : 50
        },
        create : function(options){
            this.el = this; //需要么？

            applyDefaultPara.call(this.rDefaults,Tianzi.Square,this,options);
            this.rElmt = paper.rect().attr(this.el.rDefaults);  //按照外观的默认值构建   先用raphael的rect 以后可能会改成一个单独绘图函数
            this.rElmt.TZBindObj = this;
            squareBox.push(this);
            this.id = _.last(squareBox).id + 1;

            this.rElmt.click(function(){
                this.TZBindObj.click();  //这里的this指向的是Raphael??
            });   //如果不用call的话，el.click的上下文会比较混乱？？

            this.rElmt.mouseover(function(){
                this.TZBindObj.mousein();
            });   //如果不用call的话，el.click的上下文会比较混乱？？

        },
        changeAppearence : function(options){
//            _.map(options,function(){  暂时不用每条都检查
            console.log(options);
                this.rElmt.attr(options);
//            })
        },
        freeze : function(){},
        click : function(){
            console.log('sqr clicked');
//            console.log(this.rElmt.getBBox());

        },
        mousein : function(){
//            console.log('mouse in');
            console.log(this.rElmt);

        },
        mouseout : function(){}


    };
    /**
     *
     * 显示的文字
     *  @desc
     *  @param {Object}
     *
     */
    TianZi.Text = function(options){
        this.create(options);
        return this;
    }
    TianZi.Text.prototype = {
        textId : 0 ,
        rElmt : null,
        relatedSquare : null,
        create : function(options){}
    }

    init = function(){
//                console.log(this);
        var firstBoard = new Tianzi.Board();
        var sqr = new Tianzi.Square();

    };


    init();

}

function applyDefaultPara(theClassDefault,theObj,options){
//            console.log('applyDefaultToSubstance start');
    _.map(theClassDefault,function(val,key,list){
//        theObj[key] =   || val;
    });

}


 //获取鼠标位置 原生方法 暂定

///**
// * 获取鼠标在页面上的位置
// * @param ev		触发的事件
// * @return			x:鼠标在页面上的横向位置, y:鼠标在页面上的纵向位置
// */
//function getMousePoint(ev) {
//    // 定义鼠标在视窗中的位置
//    var point = {
//        x:0,
//        y:0
//    };
//
//    // 如果浏览器支持 pageYOffset, 通过 pageXOffset 和 pageYOffset 获取页面和视窗之间的距离
//    if(typeof window.pageYOffset != "undefined") {
//        point.x = window.pageXOffset;
//        point.y = window.pageYOffset;
//    }
//    // 如果浏览器支持 compatMode, 并且指定了 DOCTYPE, 通过 documentElement 获取滚动距离作为页面和视窗间的距离
//    // IE 中, 当页面指定 DOCTYPE, compatMode 的值是 CSS1Compat, 否则 compatMode 的值是 BackCompat
//    else if(typeof document.compatMode != "undefined" && document.compatMode != "BackCompat") {
//        point.x = document.documentElement.scrollLeft;
//        point.y = document.documentElement.scrollTop;
//    }
//    // 如果浏览器支持 document.body, 可以通过 document.body 来获取滚动高度
//    else if(typeof document.body != "undefined") {
//        point.x = document.body.scrollLeft;
//        point.y = document.body.scrollTop;
//    }
//
//    // 加上鼠标在视窗中的位置
//    point.x += ev.clientX;
//    point.y += ev.clientY;
////    console.log('ccc');
//    console.log(point);
//    // 返回鼠标在视窗中的位置
//    return point;
//}
//
//document.onmousedown = function(event){
//    console.log('document click');
//    getMousePoint(event);
//}