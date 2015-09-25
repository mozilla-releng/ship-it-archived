sources = ["kickoff/static/kickoff.js", "kickoff/static/suggestions.js"];
module.exports = function(grunt) {
    grunt.initConfig({
        qunit: {
            files: ['kickoff/test/js/jstest.html']
        },
        jscs: {
            main: "ship-it.js",
            controllers: {
                src: sources,
                options: {
                    config: '.jscsrc',
                    verbose: true
                }
            }
        },
        eslint: {
            target: sources
        }
    });
    grunt.loadNpmTasks('grunt-contrib-qunit');
    grunt.loadNpmTasks('grunt-jscs');
    grunt.loadNpmTasks('grunt-eslint');
    grunt.registerTask('default', ['qunit', 'jscs', 'eslint']);
};
