sources = [
    "kickoff/static/global_config.js",
    "kickoff/static/kickoff.js",
    "kickoff/static/model/release.js",
    "kickoff/static/model/errors.js",
    "kickoff/static/treestatus.js",
    "kickoff/static/hg_mozilla.js",
    "kickoff/static/suggestions.js",
    "kickoff/static/datetime.js",
];

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
