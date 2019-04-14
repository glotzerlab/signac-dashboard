// The following code is based off a toggle menu by @Bradcomp
// source: https://gist.github.com/Bradcomp/a9ef2ef322a8e8017443b626208999c1
$(document).on('turbolinks:load', function() {
  if ( $('.navbar-burger').length && $('.navbar-menu').length ){
    var burger = document.querySelector('.navbar-burger');
    var menu = document.querySelector('.navbar-menu');
    burger.addEventListener('click', function() {
        burger.classList.toggle('is-active');
        menu.classList.toggle('is-active');
    });
  }
});
