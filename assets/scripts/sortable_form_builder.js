import Sortable from 'sortablejs';

document.addEventListener('DOMContentLoaded', function () {
  const sortable = new Sortable(document.getElementById('sortable-container'), {
    animation: 150,
    handle: '.fa-grip-lines',
    onEnd: function (evt) {
      // This is where you would send the new order to the server
      console.log('Item moved from position', evt.oldIndex, 'to', evt.newIndex);
      // You can use HTMX to send the new order to the backend
      // Example:
      // htmx.ajax('POST', '/your-endpoint/', {
      //   swap: 'none',
      //   values: {
      //     oldIndex: evt.oldIndex,
      //     newIndex: evt.newIndex,
      //     itemId: evt.item.getAttribute('data-id') // Assuming each item has a data-id attribute
      //   }
      // });
    }
  });
  document.body.addEventListener('htmx:configRequest', function (evt) {
    // Show the saving indicator
    document.getElementById('saving-indicator').classList.remove('hidden');
    document.getElementById('saved-indicator').classList.add('hidden');
  });

  document.body.addEventListener('htmx:afterRequest', function (evt) {
    // Hide the saving indicator and show the saved indicator
    document.getElementById('saving-indicator').classList.add('hidden');
    document.getElementById('saved-indicator').classList.remove('hidden');
  });
});
