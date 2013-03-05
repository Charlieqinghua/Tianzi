//逻辑和绘图应该分开   绘图先使用raphael  以后可以考虑canvas

//如果整个board大小在运行中改变（skew），default参数要随之改变么？
var paper;


$(document).ready(function(){
    var mouseToSvg;
    var svgWrapper = document.getElementById('svgWrapper');

    paper = Raphael('svgWrapper',800,600);
    tianzi = new Tianzi(paper);
    window.debug = new debug();
})


Tianzi = function(paper) {
//    var squareBox = [];
//    相关的大参数
    var BOARD_SIZE = {width : 600 , height : 600},
        squareMouseoverQueue = [{ animation:{transform:'s1.4'}, ms:150 },{ animation:{transform:'s1.1'}, ms:200 } ,{ animation:{transform:'s1.3'}, ms:200 }],
        textMouseoverQueue = [{animation:{fill:'#e0732a'}, ms:150}],  //
        textMouseoutQueue = [{animation:{fill:'#0c967e'}, ms:150}]



//    调试方便的外露部分，暂时的     以后要封装进Tianzi的闭合作用域
    window.squareBox = [];
    window.textBox = [];
    window.Tianzi = this;
    window.testWordBox = '我是一个测试DUMBman'.split('');
    window.inputBox = $('#inputBox');
    window.inputWrapper = $('#inputWrapper');

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
                paper.rect(0,0,BOARD_SIZE.width,BOARD_SIZE.height).attr({fill:"#41bea8",stroke:'none'   /*,"fill-opacity": 0.5*/})
            );
//            绑定给raphael的click函数
            this.rElmt.click(function(event){
                mouseToSvg = { offsetX:event.offsetX, offsetY:event.offsetY };
                el.click({mouseToSvg : mouseToSvg ,eventArg : event});
            })
        },
        click : function(args){
//            console.log('board click');
            point = args.mouseToSvg;
//            console.log(args.eventArg);
//            没想好封装名  单击时候按着shift键 添加格子 优先判断shift
            if(args.eventArg.shiftKey == true){
//                console.log('shift');
                var tempSqr = new Tianzi.Square({x:point.offsetX,y:point.offsetY});
                tempSqr.changeAppearence({
                        x : point.offsetX - point.offsetX % tempSqr.rDefaults.width,
                        y : point.offsetY - point.offsetY % tempSqr.rDefaults.height}
                );  // tempSqr.rDefaults这个写法麻烦， 考虑以后要不要把及时的参数放到Square.status 里面……
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
        tzDefaults : {  // 对应tianzi游戏的默认
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
            var gX = options.gridX ? options.gridX : this.tzDefaults.gridX,
                gY = options.gridY ? options.gridY : this.tzDefaults.gridY;
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
        status : {
            gridX : 0,
            gridY : 0
        },
        textStyle : {
            'font-size' : 24,
            'font-family' : '隶书', //如果没有字体怎么办？  单独写一个函数设定，也许可以下载webfont
    //                'href' : '', href 和 target 什么区别 ？   target在svg标签里的show属性是什么意思？
    //                'target' : '#inputWrapper',
            fill : '#0c967e'  //文字颜色
        },
        relatedSquare : null,
        create : function(options){
            var bBox = options.bBox || { x:0, y:0};
            var txt = options.txt || '';
            this.status = {};
            this.rElmt = paper.text( (bBox.x + bBox.x2) / 2 ,(bBox.y + bBox.y2) / 2  ,txt);  // text-anchor默认middle时是设定文字中心点坐标
            this.rElmt.TZBindObj = this;
            //事件绑定--------------------
            this.rElmt.click(function(event){
                this.TZBindObj.click({eventArg:event});

            });
            this.rElmt.mouseover(function(){
                this.stop().animateQueue(textMouseoverQueue);
                this.TZBindObj.mouseover();
            });
            this.rElmt.mouseout(function(){
                this.stop().animateQueue(textMouseoutQueue);
//                this.TZBindObj.mouseout();
            });

        },
        click : function(args){
            // 不太确定  翻来覆去麻烦
            this.relatedSquare.click({eventArg:args.eventArg});
        },
        mouseover : function(){

        }
    }

//    属于Tianzi的部分  -------------------------------------------------------------

    /**
     *
     * Tianzi的初始化
     *  @desc  对inputWrapper的事件绑定   keypress>change>blur
     *  @param {Object}
     *
     */
    init = function(){
        var firstBoard = new Tianzi.Board();
        var startList = {
            Squares : [{ gridX:4, gridY:6 },{ gridX:5, gridY:2 },{ gridX:4, gridY:8 },{ gridX:4, gridY:9 },{ gridX:4, gridY:3 }]
        }
        _.each(startList.Squares,function(val,key){
            var sqr = new Tianzi.Square({gridX:val.gridX,gridY:val.gridY });
        })
        //TODO inputBox作为dom元素的事件绑定  应该放到Tianzi里面一个合适的位置
        inputWrapper.on('click',function(event){
            inputBox[0].focus();
        })
        inputBox.on('keydown',function(event){
//            console.log(event);  //todo 找出metakey graphcikey等等的意思是什么  Esc键怎么检测？
            //检测esc
            if(event.keyCode == 27){
//                console.log('esc');
                inputWrapper.hide();
            }
            if(event.keyCode == 13){
                tianzi.refreshTxt();
                inputWrapper.hide();
            };
            //TODO  需要加入实时的ajax提醒么？
        })
        inputBox.on('blur',function(event){
                //refreshTxt 不能放在这里？ 因为按下回车后blur事件还是会触发  除非能想到办法在blur发生的时候判断之前有没有别的事件发生
            //
                inputWrapper.hide();
//                console.log(event);
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



    init();

}
Tianzi.prototype = {
    scale : 1,
    invokedObj : {
        square : null
    },
    refreshTxt : function(){  //todo  这个的存在意义是什么？
        inputWrapper.hide();
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




debug = function(){
//    return this;
}
debug.prototype = {
    printObjInfo : function(args){
        if( document.getElementById("debugInput").value != ''  ){
            //输入不为空
        }
        window.debugList = {
            squareBox : squareBox,
            textBox : textBox
        }//TODO 需要设定么？
//        {
            if(args.spercific){
                _.map(args.spercific,function(val,key){
                    console.log(val);
                })
            }
            else{
                _.map(debugList,function(val,key){
                    console.log(key);
                    console.log(val);
                })
            }
//        }
    }
}

var todoList = {
    //TODO 这种麻烦的绑定方式……   有余力的话看一下Raphael和jquery的事件实现模型  还有啊外观变化到底是绑给raphael的事件呢还是Tianzi的事件呢？
//    eve('square.click',this,'ddddddddddddd') //eve 是可以传递上下文和参数的  不过这个上下文要怎么用？
}

function saveGameData(){
    //todo 使用localstorage存储json的缺点在于  如果json对象很大， 那么每次读写都要用JSON来在字符和对象间转换 用WebSql会好点么？
    var Squares = {};
    var Texts = {};
    localStorage['Squares'] = null;
//    localStorage['Texts'] = null; // 没有独立于方框存在的字的话，就不需要这个了
//    console.log(squareBox);
    _.each(squareBox,function(item,idx){
        Squares[item.squareId] = {  gridX : item.status.gridX , gridY : item.status.gridY  };
        if(item.relatedText){
            Texts[item.relatedText.textId] = {relatedSquareId : item.squareId};
            Squares[item.squareId]['relatedTextId'] = item.relatedText.textId;
            Squares[item.squareId]['relatedTextTxt'] = item.relatedText.txt;
        }
        else {
//            Squares[item.squareId]['relatedTextId'] = null;  //null 还是数字比较好呢？
        }
//        console.log('add one aqr into Squares');
    })
    localStorage.setItem('Squares',JSON.stringify(Squares));
}

function loadGameData(){
    var squares ;
    squares = JSON.parse( localStorage.getItem('Squares'));
    console.log(squares);
}