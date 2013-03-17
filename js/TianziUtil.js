function applyDefaultPara(theClassDefault,theObj,options){
//            console.log('applyDefaultToSubstance start');
    _.each(theClassDefault,function(val,key,list){
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
    localStorage.setItem('Matrix',JSON.stringify(tianzi.board.matrix));
}

function loadGameData(){
    var squares ;
    var matrix;
    resetGame();
    squares = JSON.parse( localStorage.getItem('Squares'));
    matrix = JSON.parse( localStorage.getItem('Matrix'));
    rebuildGame({squares:squares,matrix : matrix});

//    console.log(squares);
}
function resetGame(){
    _.each(squareBox,function(item,idx){
        item.delete();
    });
    tianzi.board.refresh();
    textBox = [];
    squareBox = [];   //squareBox = textBox = []; 这样的写法不对，起码和我想要实现的意思不一样
};
function rebuildGame(data){
    var squares = data.squares;
    _.each(squares,function(item,idx){
        var sqr = new Tianzi.Square({gridX:item.gridX,gridY:item.gridY});
        if(item.relatedTextTxt){
            sqr.addText(item.relatedTextTxt);  //如果textId对于游戏进行不是很重要，就可以这样简写，否则就要改写addText考虑传入textId时的状况
        }
    });
    if(data.matrix){  tianzi.board.matrix = data.matrix  };
    var riddles = data.riddles;
    _.each(riddles,function(item,idx){
        var rdl = new Tianzi.Frame({startX:item.startX , startY:item.startY , length:item.len , direction:item.dir});

    });
};

/**
 * 使用时记住用call或者apply改变context
 * @param elmt
 * @return {Object}
 */
function getCenter(obj,type){
//    console.log(this);
    var bBox;
    if(type){
        switch(type){
            case 'bBox':{
                bBox = obj;  break;
            }
        }
    }else{//默认传raphael.Element元素
        bBox = this.getBBox(obj);
    }
    return {x:(bBox.x + bBox.x2)/2,y:(bBox.y + bBox.y2)/2};
};

/**
 * 根据在window/或者是svg中的位置 转换为在 grid中的位置
 * @param point {x:Number,y:Number}
 * @param {String[optional]}  type
 * @return {Object} {gridX:gx , gridY:gy}
 */
function getPointInGrid(point,type){ //
    var gx,gy;
//    console.log(point);
    if(type){
        switch(type){
            case 'document':{}
            case '' :{}
        }
    }else{ //默认方法  以svg位置判断
        gx = (point.x - tianzi.board.offsetToSvg.x) * tianzi.scale  /  tianzi.boardOption.gridWidth >>0;
        gy = (point.y - tianzi.board.offsetToSvg.y) * tianzi.scale / tianzi.boardOption.gridWidth >> 0; //用移位的方法实现floor？
    }
    return {gridX:gx , gridY:gy};
};
/**
 * 根据在grid中的位置 转换为在 svg中的bBox左上角坐标
 * @param {Object} gridPos
 * @param {String[optional]}  type
 * @return {Object} {x:Number , y:Number}
 */
function convertGridPosToSvg(gridPos,type){
    //todo 参数的 optional怎么在javadoc中标记出来？
    var x,y;
    if(type){
        switch(type){
            case 'document':{}
        }
    }else{ //默认方法
         x = (gridPos.gridX  *tianzi.boardOption.gridWidth + tianzi.board.offsetToSvg.x)  * tianzi.scale;
         y = (gridPos.gridY  *tianzi.boardOption.gridWidth + tianzi.board.offsetToSvg.y)  * tianzi.scale;
    }
    return {x:x,y:y};
}


function scaleGame(input,paper) {
    var scale;
    if(typeof input =='String'){
        scale = parseInt(input);
    }else{
        scale = input;
    };
    tianzi.scale = scale;
    paper.setViewBox(30,30,paper.width / scale,paper.height/scale);
}