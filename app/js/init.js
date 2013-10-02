// seajs 的简单配置
seajs.config({
  base: "./app/",
  paths: {
    "appBase": "http://localhost:8033/game/app",
    "coreDir": "http://localhost:8033/game/app/src/coffee-files"
  },
  alias: {
    "zepto": "appBase/lib/zepto.js",
//    "raphaeljs": "appBase/lib/raphael.js",
    "underscore": "appBase/lib/underscore.js",
    "angularjs": "appBase/lib/angular.min.js"
  },
  debug: true
});

// 加载入口模块
seajs.use("js/game.js",function(){
  console.log(seajs)    ;
  console.log(seajs.cache)
});
