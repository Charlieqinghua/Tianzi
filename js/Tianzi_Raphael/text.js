/**
 *
 * 显示的文字
 *
 *  @param {Object}
 *  @tips 鉴于没有独立于squre存在的text 所以最好不要直接创建，而是使用square的addText
 *
 */
Tianzi.Text = Tianzi.Component.extend({
    textId : 0 ,
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
//                console.log(event);
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
});