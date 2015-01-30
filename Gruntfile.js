module.exports = function(grunt) {
    grunt.initConfig({
        qunit: {
            files: ['kickoff/test/js/jstest.html']
        }
    });
    grunt.loadNpmTasks('grunt-contrib-qunit');
    grunt.registerTask('default', ['qunit']);
};
