document.addEventListener('DOMContentLoaded', function () {
        const durationInput = document.getElementById('duration-field');
        const unlimitedCheckbox = document.getElementById('unlimited-checkbox');

        function toggleCheckboxState() {
        // When the input is a number and the number is not 0, the checkbox is disabled and unchecked
            if (durationInput.value.trim() !== ''  && durationInput.value.trim() !== '0') {
                unlimitedCheckbox.disabled = true;
                unlimitedCheckbox.checked = false;
            } else {
                unlimitedCheckbox.disabled = false;
            }
        }

        durationInput.addEventListener('input', toggleCheckboxState);

        toggleCheckboxState();
    });