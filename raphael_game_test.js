//逻辑和绘图应该分开   绘图先使用raphael  以后可以考虑canvas

//如果整个board大小在运行中改变（skew），default参数要随之改变么？
/*todo  总备忘 Raphael.isBBoxIntersect 检测盒碰撞？    setViewbox?缩放棋盘的关键  看api
 */
//todo 文字拖动时变成搜索怎么办？ 阻止默认事件？
//todo 加入层的概念？ Raphael 原本的toFront会直接到离屏幕最近  但是游戏应该有个spritegroup的概念
var paper;


$(document).ready(function(){
    var mouseToSvg;
    var svgWrapper = document.getElementById('svgWrapper');

    paper = Raphael('svgWrapper',800,600);
    window.tianzi = new Tianzi(paper);
    tianzi.run();
    window.debug = new debug();
})


Tianzi = function(paper) {
//    var squareBox = [];
//    相关的大参数
    var BOARD_SIZE = {width : 600 , height : 600 , xGrids : 18 ,yGrids : 18, gridWidth : 40},
        squareMouseoverQueue = [{ animation:{transform:'s1.4'}, ms:150 },{ animation:{transform:'s1.1'}, ms:200 } ,{ animation:{transform:'s1.3'}, ms:200 }],
        textMouseoverQueue = [{animation:{fill:'#e0732a'}, ms:150}],  //
        textMouseoutQueue = [{animation:{fill:'#0c967e'}, ms:150}];


        // 黄色
    textMouseoverQueue = [{animation:{fill:'#e0732a'}, ms:150}],  //
    textMouseoutQueue = [{animation:{fill:'#0c967e'}, ms:150}]; 


    this.boardOption = BOARD_SIZE;


//    调试方便的外露部分，暂时的     以后要封装进Tianzi的闭合作用域
    window.squareBox = [];
    window.textBox = [];
    window.frameBox = [];
//    window.Tianzi = this;
    window.testWordBox = '我是一个测试DUMBman'.split('');
    window.inputBox = $('#inputBox');
    window.inputWrapper = $('#inputWrapper');

    var R = paper;



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
        // fillColor : "#dddd44",
        rDefaults:{
            // //蓝黄
            // fill:"#41bea8",
            // stroke:'none'

            // 黄色
            fill : '#febe28',
            stroke : 'none'
        },
        matrix : [],
        offsetToSvg : {x:20,y:20},
        refresh : function(atbt,options){
            //以后扩写时候可以甄别atbt

            this.matrix = [];
            for(var temp = 0; temp<BOARD_SIZE.xGrids ; temp++){ //初始化矩阵
                var tempRow=new Array(BOARD_SIZE.yGrids);
                this.matrix.push(tempRow);
            }
        },
        create : function(){
            var el = this;
            this.refresh();
//            console.log(this.matrix);
            this.rElmt = paper.set();
            this.rElmt.TZBindObj = this;
            this.rElmt.push(
                paper.rect(this.offsetToSvg.x,this.offsetToSvg.y,BOARD_SIZE.xGrids * BOARD_SIZE.gridWidth,BOARD_SIZE.yGrids * BOARD_SIZE.gridWidth).attr(this.rDefaults)
            );
//            绑定给raphael的click函数
            this.rElmt.click(function(event){
                mouseToSvg = { offsetX:event.offsetX, offsetY:event.offsetY };
//                console.log(mouseToSvg);
                el.click({mouseToSvg : mouseToSvg ,eventArg : event});
            });
            this.rElmt.drag(function(){})
        },
        click : function(args){
            point = args.mouseToSvg;
            //todo 考虑盘面起始位置以及scale的变化
//            console.log(args.eventArg);
//            没想好封装名  单击时候按着shift键 添加格子 优先判断shift
            if(args.eventArg.shiftKey == true){
//                console.log('shift');
                var svgPos = getPointInGrid({x:point.offsetX, y:point.offsetY});
                var tempSqr = new Tianzi.Square(svgPos);
//                var tempSqr = new Tianzi.Square({x:point.offsetX,y:point.offsetY});
//                tempSqr.changeAppearence({
//                        x : point.offsetX - point.offsetX % tempSqr.rDefaults.width,
//                        y : point.offsetY - point.offsetY % tempSqr.rDefaults.height}
//                );  // tempSqr.rDefaults这个写法麻烦， 考虑以后要不要把及时的参数放到Square.status 里面……
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
            //蓝黄
            // fill : "#f1f587",
            // stroke : '#41bea8',
            //黄色
            fill : "#f1f587",
            stroke : '#febe28',
            width : BOARD_SIZE.gridWidth,
            height :BOARD_SIZE.gridWidth
        },
        create : function(options){
            el = this; //需要么？
            this.status = {}; //注意要初始化！！！！要不然后面改单项有屁用！
            this.squareId = _.last(squareBox) ? _.last(squareBox).squareId + 1 : 1 ; //如果last的id不是最大，可能出现重叠现象
//            adjustByScale();  //TODO  是基于proto的继承呢？ 还是每个类单独写一个
            applyDefaultPara.call(this.rDefaults,Tianzi.Square,this,options);
            this.rElmt = paper.rect().attr(this.rDefaults);  //按照外观的默认值构建   先用raphael的rect 以后可能会改成一个单独绘图函数
            var gX = options.gridX ? options.gridX : this._tzDefaults.gridX,
                gY = options.gridY ? options.gridY : this._tzDefaults.gridY;
//            console.log(this.status);
            this.status.gridX = gX ,     this.status.gridY = gY;
            var newPos = convertGridPosToSvg(this.status);
//            this.rElmt.attr({x:gX * Tianzi.scale * this.rDefaults.width + Tianzi.board.offsetToSvg.x, y:gY * Tianzi.scale * this.rDefaults.height + tianzi.board.offsetToSvg.y});
            this.rElmt.attr({x:newPos.x, y:newPos.y});
            //todo 和Tianzi.scale 相关的应该还有别的东西 最好整理下
            this.rElmt.toFront();
            tianzi.board.matrix[gX][gY] = {sqrId:this.squareId};
            this.rElmt.TZBindObj = this;

            squareBox.push(this);

            this.rElmt.mouseover(function(event){
                this.stop().animateQueue(squareMouseoverQueue);
                this.toFront(); //放到最上层
                if (this.TZBindObj.relatedText) {
                    this.TZBindObj.relatedText.rElmt.toFront();
                } //文字要更上层
                this.TZBindObj.mouseover();
            });
            this.rElmt.mouseout(function(event){
                this.stop().animate({transform:'s1r0'},500);  //todo 先消失一下，整合到drag onend里
            });
            this.rElmt.onDragStart = function(dx,dy,event){
                //onstart 参数两个 距离window边缘的像素  scrollTop??   event  mouseevent
//                    click-------------
                this.TZBindObj.click({eventArg:event});  //todo 如果移动速度不大就说明仅仅是单击？？
//                    ---------------click
                this.TZBindObj.holder = paper.set(this.clone());
//                console.log(this.TZBindObj);
                this.positionOrigin = {x:parseInt(this.attr('x')) , y:parseInt(this.attr('y'))}; //positionOrigin是相对于svg的
                if(this.TZBindObj.relatedText){
                    this.textOrigin = {x:this.TZBindObj.relatedText.rElmt.attr('x'),y:this.TZBindObj.relatedText.rElmt.attr('y')};
                    this.TZBindObj.holder.push(this.TZBindObj.relatedText.rElmt.clone());
                }
                tianzi.invokedObj.draggingSetHolder = this.TZBindObj.holder;  //holer里是raphael元素

                //整合click
//                    this.TZBindObj.click({eventArg:event});
            };
            this.rElmt.onDragMove = function(dx,dy,scx,scy){
                var newLTInSvg ={  //square的左上角在svg中的位置
                    x:this.positionOrigin.x + dx ,y: this.positionOrigin.y + dy
                }
                this.attr(newLTInSvg);
                if(this.TZBindObj.relatedText){
                    this.TZBindObj.relatedText.rElmt.attr({x:this.textOrigin.x+dx, y:this.textOrigin.y+dy});
                }
                //todo 检测在棋盘上的位置 碰撞检测  碰到空的位置要标出来  波纹特效（难度啊^）？？
                //碰撞检测如果只用raphael的isBoxIntersection做 会不会振荡太久？
                this.center = getCenter.call(this,this);
                var pInGrid = getPointInGrid(this.center);  //todo 碰撞检测也要考虑mouseover以后的放大倍数
                if(tianzi.board.matrix[pInGrid.gridX][pInGrid.gridY]){
//                        console.log(tianzi.board.matrix[pInGrid.gridX][pInGrid.gridY]); //todo 这个要shake一下
//                        console.log('ocupied');
                }else{
                    //todo  出现空的框线or？？ 提示可以放入
                }
            };
            this.rElmt.onDragOver = function(event){
                //onend  这里的event好像是mouseUp事件
//                    console.log(event);
                this.stop().animate({transform:'s1r0'},500); //尝试整合
                //todo 检测在棋盘上的位置  要是没有被占据
//                this.delete(positionOrigin);  //这样写对么？
                this.center = getCenter.call(this,this);
                var newGridPos = getPointInGrid(this.center);
                if(tianzi.board.matrix[newGridPos.gridX][newGridPos.gridY]){ //已经被占据
                    //todo
                    this.animate({x:this.positionOrigin.x ,y: this.positionOrigin.y},300); //square放回旧位置    为什么会突然错位一下？有时间调试之
                    if(this.TZBindObj.relatedText){//text放回旧位置
                        this.TZBindObj.relatedText.rElmt.animate({x:this.textOrigin.x,y:this.textOrigin.y},200);
                    }

                    this.TZBindObj.holder.remove(); //删除holder

                }else{//没有被占据
                    //todo
                    var newPos = convertGridPosToSvg(newGridPos);
//                        console.log('not ocupied');
                    this.animate({x:newPos.x, y:newPos.y},200);//square移到新位置   这里异步动画需时间，所以不能在下面马上求center 否则会不准
                    //文字移到新位置
                    if(this.TZBindObj.relatedText){
//                            this.TZBindObj.relatedText.rElmt.animate({x:this.textOrigin.x,y:this.textOrigin.y});
//                            newSet.push(this.TZBindObj.relatedText.rElmt);
                        var textCenter = getCenter.call(this,
                            {x:newPos.x,y:newPos.y,x2:newPos.x+(tianzi.boardOption.gridWidth*tianzi.scale),y2:newPos.y+(tianzi.boardOption.gridWidth*tianzi.scale)}
                            ,'bBox');   //不确定   要是以后算法改了怎么办？  而且不够解耦啊这里
                        this.TZBindObj.relatedText.rElmt.animate({x:textCenter.x,y:textCenter.y},200)
                    }
//                        newSet.animate({x:newPos.x, y:newPos.y},200);//square和文字移到新位置  (PД`q。)·。'゜   不行啊 还是要算text的位置

                    this.TZBindObj.status.gridX = newGridPos.gridX ; //刷新status
                    this.TZBindObj.status.gridY = newGridPos.gridY ;
                    //刷新matrix
                    tianzi.board.matrix[newGridPos.gridX][newGridPos.gridY] = {sqrId:this.TZBindObj.sqrId};
                    var oldPos = getPointInGrid(this.positionOrigin);
                    tianzi.board.matrix[oldPos.gridX][oldPos.gridY] = null;

                }

                this.TZBindObj.holder.remove(); //删除holder
                tianzi.invokedObj.draggingSetHolder = null;
            };
            this.rElmt.drag(this.rElmt.onDragMove,
                this.rElmt.onDragStart,
                this.rElmt.onDragOver);  //onDragOver 好像跟raphael.Element下的事件名重复了

        },
        delete : function(){
            //寻找squareBox里id和自己相同的
            if (this.relatedText) {
                var rt = this.relatedText;
                this.relatedText.rElmt.remove();
                textBox = _.reject(textBox,function(obj,key){ return  obj.textId == rt.textId;      }) //从textBox里移除
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

            if( ! this.relatedText){
                var bBox = this.rElmt.getBBox();  //为什么用了el只会显示最后一个建立的box的数值？   用this才可以正确  也许因为我写的el = this 不对
//                没有文字就新建
                var tempTB = new Tianzi.Text({bBox : bBox,txt : txt});
                this.relatedText = tempTB;
                tempTB.relatedSquare = this;
//                console.log(this.status);
                tempTB.textId =  _.last(textBox) ? _.last(textBox).textId + 1 : 1;   //有没有不需要underscore的快速解决方法？
                tianzi.board.matrix[this.status.gridX][this.status.gridY]['txId'] = tempTB.textId;  //需要么？？只需要记录squareId就行了吧？
                //TODO 以后要不要扩展下，改成tempTB.textStyle.default
            }else{
                this.refreshText(txt);
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
                if(this.relatedText){
                    inputBox[0].value = this.relatedText.txt ? this.relatedText.txt : '';
                }else{
                    inputBox[0].value = '';
                }
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
     *
     *  @param {Object}
     *  @tips 鉴于没有独立于squre存在的text 所以最好不要直接创建，而是使用square的addText
     *
     */
    Tianzi.Text = function(options){
        this.create(options);

        return this;
    }
    Tianzi.Text.prototype = {
        textId : 0 ,
        rElmt : null,
        txt : '',
        status : {
            gridX : 0,
            gridY : 0
        },
        textStyle : {
            'font-size' : 24,
            'font-family' : '隶书', //如果没有字体怎么办？  单独写一个函数设定，也许可以下载webfont
            'cursor':'pointer',
            // fill : '#0c967e'  //
            fill : '#f25750'  //黄色版g
        },
        relatedSquare : null,
        create : function(options){
            var bBox = options.bBox || { x:0, y:0};
            this.txt = options.txt || '';
            this.status = {};
            this.rElmt = paper.text( (bBox.x + bBox.x2) / 2 ,(bBox.y + bBox.y2) / 2  ,this.txt);  // text-anchor默认middle时是设定文字中心点坐标
            this.rElmt.attr(this.textStyle);
            this.rElmt.toFront();
            this.rElmt.TZBindObj = this;
            textBox.push(this);
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
            this.rElmt.drag(function(event){
//                console.log('drag');
                this.drag({eventArg:event});
                console.log(event);
            });

        },
        click : function(args){
            // 不太确定  翻来覆去麻烦
            this.relatedSquare.click({eventArg:args.eventArg});
        },
        mouseover : function(){

        },
        drag : function(args){
            var event = args.eventArg;
//            this.rElmt

        }
    }

//    属于Tianzi的部分  -------------------------------------------------------------

    tianzi = this.init();
    return tianzi;
}
Tianzi.prototype = {
    scale : 1,
    board : null,
    invokedObj : {
        square : null,
        draggingSetHolder : null  //拖动的时候留在原地占位的暂时raphael.set
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


    },
    /**
     *
     * Tianzi的初始化
     *  @description  对inputWrapper的事件绑定   keypress>change>blur
     *  @param {Object}
     *
     */
    init : function(){
        this.board = new Tianzi.Board();

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
            inputWrapper.hide();
//                console.log(event);
        })
            .on('change',function(event){
//        console.log('change');
//                tianzi.refreshTxt();
            })
            .on('mousemove',function(event){
                //TODO 拖动要怎么检测？
                if(event.button == 1){
                    console.log('drag');
                }
            }) ;

        return this;

    },
    run : function(){
//        for test----------------------------
        var startList = {
            Squares : {
                1 : { gridX:4, gridY:6,relatedTextId:4,relatedTextTxt:'老' },
                2 : { gridX:9, gridY:2 },
                3 : { gridX:4, gridY:8 },
                4 : { gridX:3, gridY:9 },
                5 : { gridX:7, gridY:3 }
            }
        }
        rebuildGame({squares : startList.Squares});
//        a = new Tianzi.Frame({gridX:2,gridY:5,length:4});
    }
//---------------------------- for test

}
