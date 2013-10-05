module.exports = function( grunt ) {

    "use strict"

    // grunt plugins
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks( "grunt-contrib-jshint" );
    grunt.loadNpmTasks( "grunt-contrib-uglify" );
    grunt.loadNpmTasks( "grunt-contrib-concat" );
    // grunt.loadNpmTasks( "grunt-contrib-qunit" );
    // grunt.loadNpmTasks( "grunt-contrib-csslint" );
    // grunt.loadNpmTasks( "grunt-html" );
    // grunt.loadNpmTasks( "grunt-compare-size" );
    // grunt.loadNpmTasks( "grunt-git-authors" );

    var mountFolder = function (connect, dir) {
      return connect.static(require('path').resolve(dir));
    };

    module.exports = function(grunt){

    };

    grunt.initConfig({
        watch: {
            scripts: {
                files: ['**/*.js'],
                tasks: ['jshint'],
                options: {
                  spawn: false,
                },
            }
        },
        cancat: {

        },
        jslint: {

        },
        jshint:{
            ui: {
                options: {
                    
                },
                files: {
                    src: "app/src/*.js"
                }
            }
        },
        jasmine:{

        },
        docco: docco
    });
    // var coffeeFiles = "app/src/coffee-files/*.coffee"
    // var docco = function() {
    //     // body...
    // }
    //grunt.registerTask( "watch", [ "watch"] );
    grunt.registerTask( "lint", [ "jslint"] );
    grunt.registerTask( "test", [ "jasmine"] );
    grunt.registerTask( "my_watch", [ "watch"] );
    grunt.registerTask( "makedoc", [ "docco"] );

}
