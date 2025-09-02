/**
 * @file Manages the functionality for the main header dropdown menu.
 * This includes handling the logic to close the menu when a user clicks outside of it.
 */

/**
 * Initializes the dropdown menu functionality.
 * It finds the necessary elements and adds an event listener to the document
 * that closes the menu if a click occurs outside of the menu panel or its trigger button.
 */
function initDropdownMenu() {
    // Find all required elements for the menu to function.
    const sidebarToggle = document.getElementById('sidebar-toggle-checkbox');
    const sidebarMenu = document.querySelector('.sidebar-menu');
    const sidebarTrigger = document.querySelector('.sidebar-trigger');

    // If any of the essential elements are missing, abort to prevent errors.
    // This makes the script safe to run on pages without a dropdown menu.
    if (!sidebarToggle || !sidebarMenu || !sidebarTrigger) {
        return;
    }

    // Add a single 'mousedown' event listener to the entire document.
    // 'mousedown' is used instead of 'click' to reliably prevent race conditions
    // where the menu closes immediately after being opened.
    document.addEventListener('mousedown', function (event) {
        // Only run the logic if the menu is currently open (checkbox is checked).
        if (sidebarToggle.checked) {
            
            // Check if the click occurred inside the menu panel.
            const isClickInsideMenu = sidebarMenu.contains(event.target);
            
            // Check if the click occurred on the trigger button (or its icons).
            const isClickOnTrigger = sidebarTrigger.contains(event.target);

            // If the click was outside of both the menu and its trigger, close the menu.
            if (!isClickInsideMenu && !isClickOnTrigger) {
                sidebarToggle.checked = false;
            }
        }
    });
}

// Export the function to make it available for import in other modules (e.g., main.js).
export { initDropdownMenu };