//逻辑和绘图应该分开   绘图先使用raphael  以后可以考虑canvas

//如果整个board大小在运行中改变（skew），default参数要随之改变么？
var paper;


$(document).ready(function(){
    var mouseToSvg;
    var svgWrapper = document.getElementById('svgWrapper');

    paper = Raphael('svgWrapper',800,600);
    tianzi = new Tianzi(paper);


})


Tianzi = function(paper) {
//    var squareBox = [];
//    相关的大参数
    var BOARD_SIZE = {width : 600 , height : 600};


//    调试方便的外露部分，暂时的     以后要封装进Tianzi的闭合作用域
    window.squareBox = [];
    window.textBox = [];
    window.Tianzi = this;
    window.testWordBox = '我是一个测试DUMBman'.split('');
    window.inputBox = $('#inputBox');
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
            cy : 0,
            invoked : false
        },
        rElmt : null,
        relatatedText : null,
        rDefaults : {    //主要是为了给raphael用  以后外观和内在要分开
            fill : "#a4d",
            stroke : '#eee',
            width : 50,
            height :50,
            x : 50,
            y : 50
        },
        create : function(options){
            el = this; //需要么？

            applyDefaultPara.call(this.rDefaults,Tianzi.Square,this,options);
            this.rElmt = paper.rect().attr(el.rDefaults);  //按照外观的默认值构建   先用raphael的rect 以后可能会改成一个单独绘图函数
            this.rElmt.TZBindObj = this;
            this.id = _.last(squareBox) ? _.last(squareBox).id + 1 : 1 ;
            squareBox.push(this);

            this.rElmt.click(function(event){
                this.TZBindObj.click(event);  //这里的this指向的是Raphael??
            });   //如果不用call的话，el.click的上下文会比较混乱？？
            eve.on('square.click',function(word){
//                console.log(word);
            })
            this.rElmt.mouseover(function(event){
//                console.log(this);

                //TODO 这种麻烦的绑定方式……   有余力的话看一下Raphael和jquery的事件实现模型  还有啊外观变化到底是绑给raphael的事件呢还是Tianzi的事件呢？
                eve('square.click',this,'ddddddddddddd'); //eve 是可以传递上下文和参数的  不过这个上下文要怎么用？

                this.TZBindObj.mousein();
            });   //如果不用call的话，el.click的上下文会比较混乱？？

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
                var tempTB = new Tianzi.Text({bBox : bBox});
                this.relatedText = tempTB;
                tempTB.relatedSquare = this;

                tempTB.textId =  _.last(textBox) ? _.last(textBox).textId + 1 : 1;   //有没有不需要underscore的快速解决方法？
//            console.log(el.rElmt.id);


                tempTB.rElmt.attr(tempTB.textStyle); //TODO 以后要不要扩展下，改成tempTB.textStyle.default
                textBox.push(tempTB);
            }
        },
        refreshText : function(newTxt){
            if(! this.relatedText){
                this.addText(newTxt);
            }
            else{
                this.relatedText.rElmt.attr({text : newTxt});
            }

            //TODO 这里不懂用jquery和zepto解决，它们好像只能提出值，不能设定值？
            document.getElementById('inputBox').value = this.relatedText.rElmt.attr('text');
            console.log('word refreshed');
        },
        /**
         * 空的框被单击后    添加文字
         *
         */
        click : function(event){
//            console.log('sqr clicked');
            this.status.invoked = true;
            tianzi.invokedObj.square = this;
//            console.log(tianzi);
            inputBox.show().css({top: event.pageY - 20 ,left:event.pageX - 20});
        },
        mousein : function(){
//            console.log('mouse in');
//            console.log(this.rElmt);

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
    Tianzi.Text = function(options){
        this.create(options);
        
        return this;
    }
    Tianzi.Text.prototype = {
        textId : 0 ,
        rElmt : null,
        textStyle : {
            'font-size' : 24,
            'font-family' : '微软雅黑',
    //                'href' : '', href 和 target 什么区别 ？   target在svg标签里的show属性是什么意思？
    //                'target' : '#inputWrapper',
            fill : '#1c5'
        },
        relatedSquare : null,
        create : function(options){
//            this.rElmt = paper.text();
            bBox = options.bBox || { x:0, y:0};
            this.rElmt = paper.text( (bBox.x + bBox.x2) / 2 ,(bBox.y + bBox.y2) / 2  ,txt);  // text-anchor默认middle时是设定文字中心点坐标
            this.rElmt.TZBindObj = this;
            this.rElmt.click(function(){
                this.TZBindObj.click();
            });

        },
        click : function(){
            // 不太确定  翻来覆去麻烦
            this.relatedSquare.click();
        }
    }

//    属于Tianzi的部分  -------------------------------------------------------------

    /**
     *
     * Tianzi的初始化
     *  @desc  对inputBox的事件绑定   keypress>change>blur
     *  @param {Object}
     *
     */
    init = function(){
//                console.log(this);
        var firstBoard = new Tianzi.Board();
        var sqr = new Tianzi.Square();

        //TODO inputBox作为dom元素的事件绑定  应该放到Tianzi里面一个合适的位置
        inputBox.on('click',function(event){
//        console.log(this);
//        console.log(event);
        })
        inputBox.on('keypress',function(event){
            //检测回车
            if(event.keyCode == 13){
//                inputBox.trigger('change');
                tianzi.refreshTxt();
                inputBox.hide();
            };
            //TODO  需要加入实时的ajax提醒么？
        })
        .on('blur',function(){
                //refreshTxt 不能放在这里？ 因为按下回车后blur事件还是会触发  除非能想到办法在blur发生的时候判断之前有没有别的事件发生
                inputBox.hide();
        })
        .on('change',function(event){
//        console.log('change');
//                tianzi.refreshTxt();
        })
        .on('mousemove',function(event){
//        console.log('drag');
            //TODO 拖动要怎么检测？
            if(event.button == 1){
                console.log('drag');
            }
        }) ;

        return this;

    };
    debug = function(){

    }


    init();

}
Tianzi.prototype = {
    invokedObj : {
        square : null
    },
    refreshTxt : function(){
        inputBox.hide();
        var ivObj = tianzi.invokedObj.square;
//        console.log(ivObj);
        var val = inputBox.val().split('');
        if(val.length > 1){
            //TODO 提示不能输入多个字  tooltip  然后 ( 禁止文字改变 / 或者只取第一个字) 不过还是要提示
            console.log('only one word');
        }
        ivObj.refreshText(inputBox.val()[0]);
        ivObj.status.invoked = false;
        tianzi.invokedObj.square = null;


    }
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