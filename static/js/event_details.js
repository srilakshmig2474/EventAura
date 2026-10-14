/* ============================================================
   SMART EVENT CERTIFICATE PLATFORM
   EVENT DETAILS JAVASCRIPT
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    console.log("Smart Event Certificate Platform JS loaded.");

    /* ========================================================
       1. CERTIFICATE COUNTER
       ======================================================== */

    const certificateSelects = document.querySelectorAll(
        ".certificate-select"
    );

    const certificateCounter =
        document.querySelector(".certificate-counter strong");

    function updateCertificateCounter() {

        if (!certificateCounter) {
            return;
        }

        let selectedCount = 0;

        certificateSelects.forEach(function (select) {

            if (
                select.value &&
                select.value.toLowerCase() !== "none" &&
                select.value.toLowerCase() !== "no certificate" &&
                select.value !== ""
            ) {
                selectedCount++;
            }

        });

        certificateCounter.textContent = selectedCount;
    }


    certificateSelects.forEach(function (select) {

        select.addEventListener(
            "change",
            updateCertificateCounter
        );

    });


    updateCertificateCounter();


    /* ========================================================
       2. CERTIFICATE TYPE VISUAL FEEDBACK
       ======================================================== */

    certificateSelects.forEach(function (select) {

        function updateSelectStyle() {

            select.classList.remove(
                "merit-selected",
                "participation-selected"
            );

            const value =
                select.value.toLowerCase();

            if (value.includes("merit")) {

                select.classList.add(
                    "merit-selected"
                );

            }

            if (value.includes("participation")) {

                select.classList.add(
                    "participation-selected"
                );

            }

        }

        select.addEventListener(
            "change",
            updateSelectStyle
        );

        updateSelectStyle();

    });


    /* ========================================================
       3. AI DESIGNER
       ======================================================== */

    const designForm =
        document.querySelector("#ai-design-form");

    const generateDesignButton =
        document.querySelector("#generate-design-button");

    const aiStatus =
        document.querySelector("#ai-status");

    const aiResult =
        document.querySelector("#ai-design-result");


    if (designForm) {

        designForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();

                if (generateDesignButton) {

                    generateDesignButton.disabled = true;

                    generateDesignButton.innerHTML =
                        "✨ Generating Design...";
                }


                if (aiStatus) {

                    aiStatus.style.display =
                        "block";

                    aiStatus.textContent =
                        "Gemini is selecting a certificate design based on your event...";
                }


                /*
                 * If your Flask backend provides an AI endpoint,
                 * the form can submit to that endpoint.
                 *
                 * For now this JavaScript safely handles the
                 * frontend loading state.
                 */

                setTimeout(function () {

                    if (generateDesignButton) {

                        generateDesignButton.disabled =
                            false;

                        generateDesignButton.innerHTML =
                            "✨ Generate AI Design";
                    }


                    if (aiStatus) {

                        aiStatus.textContent =
                            "AI design request completed.";
                    }

                }, 1200);

            }
        );

    }


    /* ========================================================
       4. DESIGN OPTION CHANGE
       ======================================================== */

    const designOptions =
        document.querySelectorAll(
            ".design-option select"
        );


    designOptions.forEach(function (select) {

        select.addEventListener(
            "change",
            function () {

                console.log(
                    "Design option changed:",
                    select.name,
                    select.value
                );

            }
        );

    });


    /* ========================================================
       5. GENERATE CERTIFICATES BUTTON
       ======================================================== */

/* ========================================================
   5. GENERATE CERTIFICATES BUTTON
   ======================================================== */

const generateButton = document.querySelector("#generateButton");
const certificateForm = document.querySelector("#certificateForm");

if (certificateForm) {
    certificateForm.addEventListener("submit", function (event) {
        const selectedCount = Array.from(
            certificateForm.querySelectorAll(".certificate-select")
        ).filter(function (select) {
            return (
                select.value === "Merit" ||
                select.value === "Participation"
            );
        }).length;

        if (selectedCount === 0) {
            event.preventDefault();
            alert("Please select Merit or Participation for at least one participant.");
            return;
        }

        const confirmed = window.confirm(
            "Generate " + selectedCount + " certificate(s) now?"
        );

        if (!confirmed) {
            event.preventDefault();
            return;
        }

        // Do not prevent submission after confirmation.
        // The browser should send the POST request to Flask.
        if (generateButton) {
            generateButton.disabled = true;
            generateButton.textContent = "Generating Certificates...";
        }
    });
}



    /* ========================================================
       6. EMAIL BUTTON
       ======================================================== */

/* ========================================================
   6. EMAIL BUTTON
   ======================================================== */

const emailButton = document.querySelector(".email-button");

if (emailButton) {
    const emailForm = emailButton.closest("form");

    if (emailForm) {
        emailForm.addEventListener("submit", function (event) {
            const confirmed = window.confirm(
                "Do you want to send the generated certificates by email?"
            );

            if (!confirmed) {
                event.preventDefault();
                return;
            }

            emailButton.disabled = true;
            emailButton.textContent = "📧 Sending Emails...";

            // Do not prevent the form submission here.
            // The browser must send the POST request to Flask.
        });
    }
}


    /* ========================================================
       7. TABLE ROW HIGHLIGHT
       ======================================================== */

    const tableRows =
        document.querySelectorAll(
            ".modern-table tbody tr"
        );


    tableRows.forEach(function (row) {

        row.addEventListener(
            "click",
            function () {

                tableRows.forEach(
                    function (otherRow) {

                        otherRow.classList.remove(
                            "selected-row"
                        );

                    }
                );


                row.classList.add(
                    "selected-row"
                );

            }
        );

    });


    /* ========================================================
       8. AUTO HIDE FLASH MESSAGES
       ======================================================== */

    const flashMessages =
        document.querySelectorAll(
            ".flash-message"
        );


    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition =
                "opacity 0.5s ease, transform 0.5s ease";

            message.style.opacity = "0";

            message.style.transform =
                "translateY(-5px)";


            setTimeout(function () {

                message.remove();

            }, 500);

        }, 5000);

    });


    /* ========================================================
       9. CONFIRM BEFORE FORM SUBMISSION
       ======================================================== */


    /* ========================================================
       10. SMOOTH SCROLL
       ======================================================== */

    const navigationLinks =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    navigationLinks.forEach(function (link) {

        link.addEventListener(
            "click",
            function (event) {

                const targetId =
                    link.getAttribute("href");

                if (
                    !targetId ||
                    targetId === "#"
                ) {

                    return;

                }


                const target =
                    document.querySelector(
                        targetId
                    );


                if (target) {

                    event.preventDefault();

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }

            }
        );

    });


    /* ========================================================
       11. PREVENT DOUBLE CLICK
       ======================================================== */

    const actionButtons =
        document.querySelectorAll(
            "[data-prevent-double-click]"
        );


    actionButtons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                if (button.dataset.clicked === "true") {

                    return;

                }


                button.dataset.clicked =
                    "true";


                setTimeout(function () {

                    button.dataset.clicked =
                        "false";

                }, 3000);

            }
        );

    });


    /* ========================================================
       12. AI DESIGN RESULT
       ======================================================== */

    function showAIDesignResult(data) {

        if (!aiResult) {
            return;
        }


        aiResult.style.display =
            "block";


        if (typeof data === "object") {

            aiResult.innerHTML = `

                <div class="ai-result-inner">

                    <strong>
                        ✨ AI Certificate Design
                    </strong>

                    <div class="ai-result-grid">

                        <div>
                            <span>Theme</span>
                            <b>${data.theme || "AI Selected"}</b>
                        </div>

                        <div>
                            <span>Style</span>
                            <b>${data.style || "Modern"}</b>
                        </div>

                        <div>
                            <span>Primary Color</span>
                            <b>${data.primary_color || "AI Selected"}</b>
                        </div>

                        <div>
                            <span>Secondary Color</span>
                            <b>${data.secondary_color || "AI Selected"}</b>
                        </div>

                    </div>

                </div>

            `;

        }

    }


    /*
     * Make the function available globally.
     * Flask/AJAX code can use it later.
     */

    window.showAIDesignResult =
        showAIDesignResult;


    /* ========================================================
       13. INITIALIZATION COMPLETE
       ======================================================== */

    console.log(
        "✓ Event Details frontend initialized successfully."
    );

});