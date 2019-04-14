$(document).on('turbolinks:load', function() {
  $('form.document-editor-form').submit(function(event) {
    // Stop form from submitting normally
    event.preventDefault();

    // Get some values from elements on the page
    var $form = $(this);
    var $result = $form.find('.document-editor-result');
    var url = $form.attr('action');

    // Clear the current result
    $form.find('.document-editor-result').html('');

    // Get each input of the form
    var formdata = {};
    $form.find(':input').each(function(index){
      var name = $(this).attr('name');
      var value = $(this).val();
      formdata[name] = value;
    });


    // Send the data using post, show the result message
    var posting = $.post(url, formdata, function(data) {
      $result.html(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
      $errorMessage = $("<span>").addClass('has-text-danger');
      $errorMessage.html(jqXHR.responseText);
      $result.html($errorMessage);
    });
  });
});
