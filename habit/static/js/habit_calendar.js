
    document.addEventListener("DOMContentLoaded", function () {
        const form = document.getElementById("calendar-form");
        const dayInput = document.getElementById("selected-day");
        const actionInput = document.getElementById("selected-action");

        const month = "{{ month }}";
        const year = "{{ year }}";

        if (!form.querySelector("input[name='month']")) {
            const monthInput = document.createElement("input");
            monthInput.type = "hidden";
            monthInput.name = "month";
            monthInput.value = month;
            form.appendChild(monthInput);
        }
        if (!form.querySelector("input[name='year']")) {
            const yearInput = document.createElement("input");
            yearInput.type = "hidden";
            yearInput.name = "year";
            yearInput.value = year;
            form.appendChild(yearInput);
        }

        document.querySelectorAll(".day-button").forEach(button => {
            button.addEventListener("click", function () {
                const currentStatus = this.dataset.status;
                const day = this.dataset.day;

                let newStatus;
                if (currentStatus === "done") newStatus = "not_done";
                else if (currentStatus === "not_done") newStatus = "none";
                else newStatus = "done";

                dayInput.value = day;
                actionInput.value = newStatus;

                form.submit();
            });
        });
    });