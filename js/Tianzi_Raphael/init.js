define(function(require, exports, module){

        var Tianzi = require('Tianzi');
    seajs.use('./js/Tianzi_Raphael/init', function(init) {
        console.log(init);
        init.init();
    });
    seajs.config({
        // 别名配置
        alias: {
            'jquery': 'js/jquery-1.7.2.js',
            'Tianzi' : 'Tianzi_Raphael/Tianzi.js',
            'square' : 'Tianzi_Raphael/square.js',
            'text' : 'Tianzi_Raphael/text.js',
            'init' : 'Tianzi_Raphael/init.js'
        },
        // 路径配置
        paths: {
//                'Tianzi_Raphael': 'js/Tianzi_Raphael'
        },
        // 调试模式
        debug: true
    });

    $(document).ready(function(){
        $('#svgWrapper').live('click',function(event){
//                console.log(event.offsetX);
//                console.log(event);
//                mouseToSvg = {
//                    x : event.offsetX,
//                    y : event.offsetY
//                }
        })
    });
    console.log(Tianzi);
        $(document).ready(function(){
            var svgWrapper = document.getElementById('svgWrapper');

            window.paper = Raphael('svgWrapper',800,600);
            tianzi = new Tianzi.Tianzi(paper);
            window.debug = new debug();
        })


    exports  = this;
});

//如果整个board大小在运行中改变（scale），default参数要随之改变么？





