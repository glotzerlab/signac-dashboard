/* NProgress, (c) 2013, 2014 Rico Sta. Cruz - http://ricostacruz.com/nprogress
 * @license MIT */

$(document).on('turbolinks:click', function() {
  NProgress.start();
});
$(document).on('turbolinks:render', function() {
  NProgress.done();
  NProgress.remove();
});
