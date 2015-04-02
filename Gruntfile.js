module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jasmine: {
            bob: {
                options: {
                    specs: 'bob/tests/js/*.js',
                    template: require('grunt-template-jasmine-requirejs'),
                    templateOptions: {
                        requireConfig: {
                            baseUrl: './bob/static/',
                            paths: {
                                'bootstrap': 'bootstrap/js/bootstrap',
                                'bootstrap-datepicker': 'bootstrap/js/bootstrap-datepicker'
                            }
                        }
                    }
                }
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-jasmine');
}
