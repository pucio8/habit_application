/**
 * @file Initializes the interactive color preview for the habit form.
 */

/**
 * Finds the color selector dropdown and a preview element in the DOM.
 * It sets the initial preview color and adds an event listener to update
 * the preview in real-time as the user selects a new color.
 */
function initHabitForm() {
    // Get the necessary DOM elements.
    const colorSelect = document.getElementById('id_color');
    const colorPreview = document.getElementById('color-preview-swatch');

    // Proceed only if both elements are found on the page.
    if (colorSelect && colorPreview) {
        
        // A function to update the preview swatch's background color.
        function updateColorPreview() {
            colorPreview.style.backgroundColor = colorSelect.value;
        }

        // Set the initial color preview when the page loads.
        updateColorPreview();
        
        // Add a listener to update the color whenever the selection changes.
        colorSelect.addEventListener('change', updateColorPreview);
    }
}

export { initHabitForm };