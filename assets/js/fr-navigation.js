/* Native disclosure navigation: usable without JavaScript or stored preferences. */
(function () {
  'use strict';
  var menus = Array.from(document.querySelectorAll('[data-disclosure-menu]'));
  function closeOthers(active) {
    menus.forEach(function (menu) { if (menu !== active) menu.open = false; });
  }
  menus.forEach(function (menu) {
    menu.addEventListener('toggle', function () { if (menu.open) closeOthers(menu); });
    menu.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
        event.preventDefault();
      }
    });
  });
  document.addEventListener('click', function (event) {
    menus.forEach(function (menu) { if (!menu.contains(event.target)) menu.open = false; });
  });
  document.addEventListener('focusin', function (event) {
    menus.forEach(function (menu) { if (!menu.contains(event.target)) menu.open = false; });
  });
}());
