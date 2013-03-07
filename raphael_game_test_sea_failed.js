

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

