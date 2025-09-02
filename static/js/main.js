/**
 * @file Main application entry point.
 * This script initializes global components and dynamically loads page-specific
 * modules to improve performance.
 */

// Import modules that are needed on every page (global components).
import { initDropdownMenu } from './components/dropdown_menu.js';
import { initAutoCloseAlerts } from './components/alerts.js';

// Wait for the DOM to be fully loaded before running any scripts.
document.addEventListener('DOMContentLoaded', function () {
    
    // Initialize components that are present on all pages.
    initDropdownMenu();
    initAutoCloseAlerts();

    // ======================================================================
    // DYNAMIC MODULE LOADING (CODE SPLITTING)
    //
    // This pattern improves initial page load performance by only loading
    // larger, specialized JavaScript modules on the pages where they are
    // actually needed.
    // ======================================================================

    // Condition 1: Load the interactive calendar module if its container exists.
    if (document.getElementById('calendar-form')) {
        import('./components/habit_calendar.js')
            .then(module => {
                // Once the module is fetched and parsed, run its initializer.
                module.initHabitCalendar();
            })
            .catch(err => console.error("Failed to load interactive calendar module:", err));
    }

    // Condition 2: Load the habit form module if a key element from that form exists.
    if (document.getElementById('color-preview-swatch')) {
        import('./components/habit_form.js')
            .then(module => {
                // Once loaded, initialize the form's interactive elements.
                module.initHabitForm();
            })
            .catch(err => console.error("Failed to load habit form module:", err));
    }
});