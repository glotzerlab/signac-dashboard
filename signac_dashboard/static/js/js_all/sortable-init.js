// Initialize Sortable for tile rearranging
$(document).on('turbolinks:load', function() {
  var el = document.querySelectorAll('.tile.is-parent.is-vertical');
  el.forEach(function(element) {
    // Check if already initialized to avoid duplicates
    if (!element.sortableInstance) {
      element.sortableInstance = new Sortable(element, {
        group: 'shared', animation: 150
      });
    }
  });
});
