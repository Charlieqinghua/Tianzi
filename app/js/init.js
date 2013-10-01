// seajs 的简单配置
seajs.config({
  base: "/app/js/",
  alias: {
    "zepto": "../lib/zepto.js",
    "underscore": "../lib/underscore.js",
    "angularjs": "../lib/angular.min.js",
    "tianzi_game_main": "../src/tianzi_main.js"
  }
});

// 加载入口模块
seajs.use("/app/js/game");
