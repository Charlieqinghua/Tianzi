//逻辑和绘图应该分开   绘图先使用raphael  以后可以考虑canvas

//如果整个board大小在运行中改变（skew），default参数要随之改变么？
/*todo  总备忘 Raphael.isBBoxIntersect 检测盒碰撞？    setViewbox?缩放棋盘的关键  看api
 */

 //todo 这种笨拙的全局变量污染如何结束？
//todo 文字拖动时变成搜索怎么办？ 阻止默认事件？
//todo 加入层的概念？ Raphael 原本的toFront会直接到离屏幕最近  但是游戏应该有个spritegroup的概念
var paper;
BOARD_SIZE = {width : 600 , height : 600 , xGrids : 18 ,yGrids : 18, gridWidth : 40};
// 黄色
textMouseoverQueue = [{animation:{fill:'#e0732a'}, ms:150}],  //
textMouseoutQueue = [{animation:{fill:'#0c967e'}, ms:150}];
squareMouseoverQueue = [{ animation:{transform:'s1.4'}, ms:150 },{ animation:{transform:'s1.1'}, ms:200 } ,{ animation:{transform:'s1.3'}, ms:200 }],
textMouseoverQueue = [{animation:{fill:'#e0732a'}, ms:150}],  //
textMouseoutQueue = [{animation:{fill:'#0c967e'}, ms:150}];


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
     * @parent {Object} Tianzi.Coomponent
     * @return {*}
     */
    Tianzi.Board = Tianzi.Component.extend({
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
            this.rElmt = paper.set();
            this.rElmt.TZBindObj = this;
            this.rElmt.push(
                paper.rect(this.offsetToSvg.x,this.offsetToSvg.y,BOARD_SIZE.xGrids * BOARD_SIZE.gridWidth,BOARD_SIZE.yGrids * BOARD_SIZE.gridWidth).attr(this.rDefaults)
            );
//            绑定给raphael的click函数
            this.rElmt.click(function(event){
                console.log(event);
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
    })

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
                1 : { gridX:4, gridY:6 },
                2 : { gridX:9, gridY:2,relatedTextId:4,relatedTextTxt:'老' },
                3 : { gridX:4, gridY:8 },
                4 : { gridX:3, gridY:9 },
                5 : { gridX:7, gridY:3 }
            },
            Riddles : {
                1 : { startX:6 , startY:5 , len:4 , dir:'H',desc : '这个'},
                2 : { startX:4 , startY:3 , len:6, dir:'V',desc : 'dd个'},
                3 : { startX:10 , startY:9 , len:4 , dir:'V',desc : '这个'}
            }
        }
        rebuildGame({Squares : startList.Squares ,Riddles:startList.Riddles});
//        a = new Tianzi.Frame({gridX:2,gridY:5,length:4});
    }
//---------------------------- for test

}

/**
 * Tianzi中所有有Raphael显示的元素的父类  检测create方法并执行
 * @type {MyClass}
 *
 */
Tianzi.Component = MyClass.extend({
    //todo 让大家都继承这个类，实现基本的调试功能  使用John 的简单继承法
    init : function(options){
        if(this.create)   this.create(options);
    },
    rElmt : null,
    /**
     * 传入需要查询的属性名列表
     * @param list  一个数组 元素是表示属性名的字符串
     */
    debug : function(list){
        _.each(list,function(item,index){
            console.log(el[item.toString()]);//巨诡异的实现法，脑子被门夹了吧我！！
        })
    }
});

