dirs =
  tmp: ".tmp"
  src: "src"
  build: "build"
  assets: "/assets"
  bower: "bower_components"
  sass: "<%= dir.assets %>/_scss"
  css: "<%= dir.assets %>/css"
  images: "<%= dir.assets %>/img"
  srcJs: "src/scripts"
  srcLess: "src/styles"
  outJs: "<%= dir.build %>/scripts"
  outCss: "<%= dir.build %>/styles"

module.exports = (grunt)->

  # load all grunt tasks
  matchdep = require("matchdep").filterDev("grunt-*").forEach grunt.loadNpmTasks

  grunt.initConfig
    dir: dirs
    pkg: grunt.file.readJSON("package.json")
    # Clean
    clean:
      build:
        files: [
          dot: true
          src: [
            ".sass-cache"
            "<%= dir.tmp %>"
            "build"
          ]
        ]

    autoprefixer:
      options:
        browsers: [
          "last 2 version"
          "safari 6"
          "ie 9"
          "opera 12.1"
          "ios 6"
          "android 4"
          "> 1%"
        ]

      build:
        src: "<%= dir.build %><%= dir.css %>/*.css"

    ###
    Uglify (minify) JavaScript files
    Compresses and minifies all JavaScript
    Usemin import .js files
    ###
    uglify:
      options:
        banner: "<%= tag.banner %>"
        sourceMap: "<%= dir.build %><%= dir.js %>/script.map"
        beautify: true

    ## less
    less:
      build:
        #files: ['<%= dir.srcLess %>/**/*.less']
        files: ()->
          ['<%= dir.srcLess %>/**/*.less']
        options:
          soureMap: true

    ## Coffee
    coffee:
      build:
        #files: ['<%= dir.coffee %>/**/*.coffee']
        expand: true
        cwd: '<%= dir.srcJs %>'
        src: ['**/*.coffee']
        dest: '<%= dir.outJs %>'
        ext: '.js'
        options:
          sourceMap: true


    ## Watch
    watch:
      #less:
        #files: ['<%= dir.srcSass %>/**/*.{sass,scss}', '!<%= dir.srcSass %>/.sass-cache/*']
        #tasks: ['less']
      scripts:
        files: ['<%= dir.srcJs %>/**/*.coffee']
        tasks: ['newer:coffee']
      #hbs:
        #files: ['src/**/*.hbs']
        #tasks: ['newer:handlebars']
      assets:
        files: ['assets/**/*', 'lib/**/*']
        tasks: ['newer:copy']

    ## concurrent
    concurrent:
      server:
        tasks: ['watch:less', 'watch:scripts', 'watch:hbs']
        options:
          logConcurrentOutput: true

    copy:
      build:
        files: [{
          expand: true
          cwd: 'assets/'
          src: '**/*'
          dest: '<%= dir.build %>/'
        },
        #{
          #expand: true
          #src: 'bower_components/**/*'
          #dest: '<%= dir.build %>/'
        #},
        {
          expand: true
          src: 'lib/**/*'
          dest: '<%= dir.build %>/'
        },
        #,{
          #src: 
        #}
        ]


  ###
  Build task
  Run `grunt build` on the command line
  Compile and compress everything
  ###
  grunt.registerTask "build", "Compile and compress everything", [
    "clean:build"
    #"less:build"
    "coffee:build"
    "uglify"
    "copy:build"
    "autoprefixer:build"
  ]


