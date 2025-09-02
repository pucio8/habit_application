/**
 * @file Manages the auto-hiding functionality for dismissible alerts.
 * This module finds all alerts on the page and sets a dynamic timer to close them.
 */

/**
 * Finds all dismissible Bootstrap alerts and schedules them to close.
 * Alerts with the special class 'long-timeout' will wait for 20 seconds,
 * while all others will close after 8 seconds.
 */
function initAutoCloseAlerts() {
    // Select all alerts that are designed to be dismissible.
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    
    // If no alerts are found on the page, do nothing.
    if (!alerts.length) {
        return;
    }

    alerts.forEach(function(alert) {
        // KROK 1: Ustaw domyślny czas znikania (8 sekund)
        let timeoutDuration = 5000; 

        // KROK 2: Sprawdź, czy alert ma naszą specjalną klasę "long-timeout"
        if (alert.classList.contains('long-timeout')) {
            // Jeśli tak, zmień czas na 20 sekund
            timeoutDuration = 20000; 
        }

        // KROK 3: Użyj dynamicznej zmiennej 'timeoutDuration' do ustawienia timera
        setTimeout(function() {
            // Use the Bootstrap Alert component's API to gracefully close the alert.
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, timeoutDuration);
    });
}

// Export the function to make it available for import in other modules (e.g., main.js).
export { initAutoCloseAlerts };