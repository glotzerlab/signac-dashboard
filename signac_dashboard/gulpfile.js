'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var csso = require('gulp-csso');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');

var jsfiles = ['assets/js/*.js'];
var sassfiles = ['assets/sass/app.scss'];
var images = ['assets/images/*.jpg', 'assets/images/*.png'];

gulp.task('scripts', function() {
  return gulp.src(jsfiles)
    .pipe(concat({ path: 'app.js', stat: { mode: 0o666 }}))
    .pipe(uglify())
    .pipe(gulp.dest('./static/js'));
});

gulp.task('sass', function() {
  return gulp.src(sassfiles)
    .pipe(sass().on('error', sass.logError))
    .pipe(csso())
    .pipe(gulp.dest('./static/css'));
});

gulp.task('images', function() {
  return gulp.src(images)
    .pipe(gulp.dest('./static/images'));
});

gulp.task('default', ['scripts', 'sass', 'images']);

gulp.task('watch', function () {
  var watcher = gulp.watch([].concat(jsfiles, sassfiles, images), ['default']);
  watcher.on('change', function(event) {
    console.log('File ' + event.path + ' was ' + event.type + ', running tasks...');
  });
});
