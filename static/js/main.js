// BlueApple — main.js
// Handles: flash auto-dismiss, date default, form submit guard

document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss flash messages after 4 seconds
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  // Set today as default on date inputs if empty
  document.querySelectorAll('input[type="date"]').forEach(function (el) {
    if (!el.value) {
      var today = new Date();
      var y = today.getFullYear();
      var m = String(today.getMonth() + 1).padStart(2, '0');
      var d = String(today.getDate()).padStart(2, '0');
      el.value = y + '-' + m + '-' + d;
      el.min = y + '-' + m + '-' + d;
    }
  });

  // Prevent double-submit on forms
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.65';
        btn.textContent = 'Please wait...';
      }
    });
  });

});