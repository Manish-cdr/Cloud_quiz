// CloudIQ — main.js
document.addEventListener('DOMContentLoaded', function () {

  // Show loading state on every form submit button
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type=submit]');
      if (btn && !btn.disabled) {
        btn.disabled = true;
        btn.textContent = 'Please wait...';
      }
    });
  });

  // Auto-dismiss flash messages after 4 seconds
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

});