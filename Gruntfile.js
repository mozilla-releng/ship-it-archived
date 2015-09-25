module.exports = function(grunt) {
    grunt.initConfig({
        qunit: {
            files: ['kickoff/test/js/jstest.html']
        },
        jscs: {
            main: "ship-it.js",
            controllers: {
                src: ["kickoff/static/kickoff.js", "kickoff/static/suggestions.js"],
                options: {
                    config: '.jscsrc',
                    verbose: true
                }
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-qunit');
    grunt.loadNpmTasks('grunt-jscs');
    grunt.registerTask('default', ['qunit', 'jscs']);
};
