define(function(require, exports, module){
    require('square');

    //逻辑和绘图应该分开   绘图先使用raphael  以后可以考虑canvas
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

    exports = Tianzi;
});
