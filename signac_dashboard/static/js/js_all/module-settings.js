$(document).on('turbolinks:load', function() {
  let moduleSettings = document.querySelector('#module-settings-form');
  if ( moduleSettings ) {
    $.getJSON(moduleSettings.action, function(data) {
      $.each(data, function(i, module) {
        console.log(module);
        let box = $('<div class="box">');
        let boxHeader = $('<h3 class="subtitle is-5">').text(module['_moduletype']);
        box.append(boxHeader);
        $.each(module['options'], function(name, moduleOptions) {
          let type = moduleOptions['type'];
          let description = moduleOptions['description'];
          let field = $('<div class="field is-horizontal">');
          let fieldLabel = $('<div class="field-label is-normal">')
          let cleanName =
          fieldLabel.append($('<label class="label">').text(description));
          field.append(fieldLabel);
          let fieldBody = $('<div class="field-body">');
          let fieldBodyField = $('<div class="field">');
          let control = $('<p class="control">');
          if ( type === 'str' ) {
            control.append($('<input class="input" type="text">').val(module[name]));
          } else if ( type === 'bool' ) {
            control.append($('<input type="checkbox">').prop('checked', module[name]));
          }
          fieldBodyField.append(control);
          fieldBody.append(fieldBodyField);
          field.append(fieldBody);
          box.append(field);
        });
        $(moduleSettings).append(box);
      });
    });
  }
});
