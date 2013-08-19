/* Simple JavaScript Inheritance
 * By John Resig http://ejohn.org/
 * MIT Licensed.
 */
// Inspired by base2 and Prototype
(function(){
    var initializing = false,
        fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;
    //fnTest是一正则表达式，匹配函数里是否有调_super方法。
    // The base Class implementation (does nothing)
    this.MyClass = function(){}; // 定义一个全局变量Class类/函数。

    // Create a new Class that inherits from this class
    MyClass.extend = function(prop) {
        /** 保存当前对象的原型(也就父类的原型),
         *  Class.extend()调用时this是Class，Person.extend调用时this是Person
         *  js里一切都是对象,Class函数也是对象,所以this这里是一个函数。
         */
        var _super = this.prototype;

        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        initializing = true;
        /**父类的实例作为子类的原型(典型的原型继承)
         * 但是这里实例化跟普通的生成对象不一样，这里不调用父类的init方法。
         * 类就是一模板,所以子类在以父类对象为原型的时候,不应调用初始化方法,仅仅是生成一个模板
         * 这边就是用initializing变量来标识实例父类是否是赋值给子类的原型。
         * 用闭包来隐藏了initializing 作为全局变量的污染
         */
        var prototype = new this();
        initializing = false;

        // Copy the properties over onto the new prototype
        for (var name in prop) {
            // Check if we're overwriting an existing function
            /** 当子类新方法父类中有同名函数，而且子类中调用了父类方法(函数中有_super的调用)
             *  这里使用了代理模式,在调用函数前先将this._super用tmp保存起来(也可能没有_super方法)
             *  在将this._super 赋值为父类中同名函数。调用结束再将原来的this._super还原
             */
            prototype[name] = typeof prop[name] == "function" &&
                typeof _super[name] == "function" && fnTest.test(prop[name]) ?
                (function(name, fn){
                    return function() {
                        var tmp = this._super;

                        // Add a new ._super() method that is the same method
                        // but on the super-class
                        this._super = _super[name];

                        // The method only need to be bound temporarily, so we
                        // remove it when we're done executing
                        var ret = fn.apply(this, arguments);
                        this._super = tmp;

                        return ret;
                    };
                })(name, prop[name]) :
                prop[name];
        }

        // The dummy class constructor
        function MyClass() {
            // All construction is actually done in the init method
            /**如果定义了初始化方法init，则调用init初始化
             * 注意：这里的this不是Class或者Person等类/函数对象
             * 而是实例化后的对象var p = new Person() 这里的this 是p
             */
            if ( !initializing && this.init )
                this.init.apply(this, arguments);

        }

        // Populate our constructed prototype object
        MyClass.prototype = prototype; //子类原型复制

        // Enforce the constructor to be what we expect
        MyClass.prototype.constructor = MyClass; //子类构造函数定义

        // And make this class extendable
        //定义类的继承方法,保证每个新类也都有extend.
        //这里也可写成 Class.extend = this.extend;
        MyClass.extend = arguments.callee;

        return MyClass;
    };
})();
/*
John Resig 的示范用法
var Person = Class.extend({
    init:function (isDancing) {
        this.dancing = isDancing;
    },
    dance:function () {
        return this.dancing;
    }
});
var Ninja = Person.extend({
    init:function () {
        this._super(false);
    },
    dance:function () {
        // Call the inherited version of dance()
        return this._super();
    },
    swingSword:function () {
        return true;
    }
});

var p = new Person(true);
p.dance(); // => true

var n = new Ninja();
n.dance(); // => false
n.swingSword(); // => true
*/
/*
 http://lcyangily.iteye.com/blog/1669483  该博客的分析
继承需要做到以下几点：
1.定义一个简单的结构，有一个初始化方法(生成对象时调用的函数，类似Java的构造方法)
2.子类的生成，必须要继承一个父类。
3.所有类的原型都是派生自Class.(就像Java类最终都派生自Object一样)
4.在子类中提供一种方法能访问到父类中被覆盖的方法。通过this._super().(如：在类Ninja的init方法中调用this._super()就是调用父类Person的init方法)





*/
