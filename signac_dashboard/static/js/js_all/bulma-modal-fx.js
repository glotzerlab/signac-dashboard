// The following code is based on bulma-modal-fx, released under the MIT license
// See signac_dashboard/static/scss/bulma-modal-fx for the LICENSE and README
// Source: https://github.com/postare/bulma-modal-fx

$(document).on('turbolinks:load', function() {
  // Trigger modals
  var modalFX = (function () {

    var elements = {
      target: 'data-target',
      active: 'is-active',
      button: '.modal-button',
      close: '.modal-close',
      buttonClose: '.modal-button-close',
      background: '.modal-background'
    };

    var moveModalsToBody = function() {
      var arr = document.querySelectorAll(elements.button);
      arr.forEach(function(el) {
        var modalid = el.getAttribute(elements.target);
        var modal = document.getElementById(modalid);
        document.getElementsByTagName('body')[0].appendChild(modal);
      });
    };

    var onClickEach = function (selector, callback) {
      var arr = document.querySelectorAll(selector);
      arr.forEach(function (el) {
        el.addEventListener('click', callback);
      });
    };

    var events = function () {
      onClickEach(elements.button, openModal);

      onClickEach(elements.close, closeModal);
      onClickEach(elements.buttonClose, closeAll);
      onClickEach(elements.background, closeModal);

      // Close all modals if ESC key is pressed
      document.addEventListener('keyup', function(key){
        if(key.keyCode == 27) {
          closeAll();
        }
      });
    };

    var closeAll = function() {
      var openModal = document.querySelectorAll('.' + elements.active);
      openModal.forEach(function (modal) {
        modal.classList.remove(elements.active);
      });
      unFreeze();
    };

    var openModal = function () {
      var modal = this.getAttribute(elements.target);
      freeze();
      document.getElementById(modal).classList.add(elements.active);
    };

    var closeModal = function () {
      var modal = this.parentElement.id;
      document.getElementById(modal).classList.remove(elements.active);
      unFreeze();
    };

    // Freeze scrollbars
    var freeze = function () {
      document.getElementsByTagName('html')[0].style.overflow = "hidden"
      document.getElementsByTagName('body')[0].style.overflowY = "scroll";
    };

    var unFreeze = function () {
      document.getElementsByTagName('html')[0].style.overflow = ""
      document.getElementsByTagName('body')[0].style.overflowY = "";
    };

    return {
      init: function () {
        moveModalsToBody();
        events();
      }
    }
  })();

  modalFX.init();

});
