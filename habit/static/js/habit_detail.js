document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('calendar-form');
  const buttons = document.querySelectorAll('.day-button');
  const inputDay = document.getElementById('selected-day');
  const inputAction = document.getElementById('selected-action');

  if (!form || !buttons || !inputDay || !inputAction) return;

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const day = button.getAttribute('data-day');
      let currentStatus = button.getAttribute('data-status');

      let nextStatus;
      if (currentStatus === 'none') nextStatus = 'done';
      else if (currentStatus === 'done') nextStatus = 'not_done';
      else nextStatus = 'none';

      inputDay.value = day;
      inputAction.value = nextStatus;

      form.submit();
    });
  });
});
