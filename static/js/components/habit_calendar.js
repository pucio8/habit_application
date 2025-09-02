/**
 * Initializes the interactive habit calendar functionality.
 *
 * This function attaches click event listeners to each day button on the calendar.
 * When a button is clicked, it cycles through completion states (none -> done -> not-done),
 * sends an AJAX request to the Django backend to save the change, and then
 * updates the button's appearance and the habit statistics on the page based
 * on the server's response.
 */
function initHabitCalendar() {
    // Find the main calendar container. If it doesn't exist, do nothing.
    const calendarForm = document.getElementById("calendar-form");
    if (!calendarForm) return;

    // --- 1. Gather required data from the DOM ---
    const updateUrl = calendarForm.getAttribute('action');
    const csrfToken = calendarForm.querySelector('[name=csrfmiddlewaretoken]').value;
    const monthInput = calendarForm.querySelector('[name=month]').value;
    const yearInput = calendarForm.querySelector('[name=year]').value;
    const dayButtons = document.querySelectorAll(".day-button");

    // --- 2. Attach event listeners to each interactive day button ---
    dayButtons.forEach(button => {
        // Only add listeners to buttons that are not disabled (i.e., are after the habit's start date).
        if (!button.disabled) {
            button.addEventListener("click", function () {
                const day = this.dataset.day;
                
                // --- 3. Determine the button's current status from its CSS class ---
                let currentStatus = "none";
                if (this.classList.contains("status-done")) {
                    currentStatus = "done";
                } else if (this.classList.contains("status-not-done")) {
                    currentStatus = "not-done";
                }
                
                // --- 4. Determine the next action in the cycle: (none -> done -> not-done -> none) ---
                let newAction = "done"; 
                if (currentStatus === "done") {
                    newAction = "not-done";
                } else if (currentStatus === "not-done") {
                    newAction = "none";
                }

                const dataToSend = { 
                    day: day, 
                    action: newAction, 
                    month: monthInput, 
                    year: yearInput 
                };

                // --- 5. Send the update to the server via a fetch POST request ---
                fetch(updateUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken // Required for Django's security
                    },
                    body: JSON.stringify(dataToSend)
                })
                .then(response => {
                    // Check if the HTTP response is successful.
                    if (!response.ok) {
                        throw new Error("HTTP error " + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    // --- 6. Update the UI based on the successful response from the server ---
                    if (data.status === 'success') {
                        // First, remove all old status classes from the button.
                        this.classList.remove('status-done', 'status-not-done', 'status-none');
                        // Then, add the new class returned by the server to ensure consistency.
                        this.classList.add(`status-${data.new_state}`);
                        
                        // Update the displayed statistics on the page.
                        document.getElementById('current-streak').textContent = `${data.stats.current_streak} days`;
                        document.getElementById('best-streak').textContent = `${data.stats.best_streak} days`;
                        document.getElementById('overall-score').textContent = `${data.stats.score}%`;
                    } else {
                        // Handle application-level errors returned from the server.
                        console.error("AJAX ERROR:", data.message);
                    }
                })
                .catch(error => { 
                    // Handle critical network or server errors.
                    console.error('CRITICAL AJAX ERROR:', error); 
                });
            });
        }
    });
}

// Export the function to be used in the main application entry point.
export { initHabitCalendar };