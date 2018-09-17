$(document).on('turbolinks:load', function() {
  var moduleSettings = document.querySelector('#module-settings-form');
  if ( moduleSettings ) {
    alert("Module settings found");
  }
});
