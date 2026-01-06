// Initialize Sortable for tile rearranging
function initSortable() {
  var el = document.querySelectorAll('.tile.is-parent.is-vertical');
  el.forEach(function(element) {
    // Check if already initialized to avoid duplicates
    if (!element.sortableInstance) {
      element.sortableInstance = new Sortable(element, {
        group: 'shared', animation: 150
      });
    }
  });
}
$(document).on('turbolinks:load', initSortable);
