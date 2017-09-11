$(document).on('turbolinks:load', function() {
  $('form.notes-form').submit(function(event) {
    // Stop form from submitting normally
    event.preventDefault();

    // Get some values from elements on the page:
    var $form = $(this);
    var url = $form.attr('action');

    // Get each input of the form.
    var formdata = {};
    $form.find(':input').each(function(index){
      var name = $(this).attr('name');
      var value = $(this).val();
      formdata[name] = value;
    });

    console.log(url);
    console.log(formdata);

    // Send the data using post
    var posting = $.post(url, formdata);

    // Put the results in a div
    posting.done(function(data) {
      console.log(data);
      $form.find('.notes-result').text(data);
    });
  });
});
