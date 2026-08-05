document.addEventListener("DOMContentLoaded", () => {
    // Base URL configuration (uses relative path for single-process, or http://localhost:8000 if opened on port 5500)
    const BASE_URL = window.location.port === "5500" ? "http://localhost:8000" : "";

    // DOM Elements
    const rosterListContainer = document.getElementById("roster-list");
    const studentForm = document.getElementById("student-form");
    const studentCountBadge = document.getElementById("student-count-badge");
    const errorBanner = document.getElementById("error-banner");

    const minAgeFilterInput = document.getElementById("min-age-filter");
    const applyFilterBtn = document.getElementById("apply-filter-btn");
    const clearFilterBtn = document.getElementById("clear-filter-btn");

    const sortFieldSelect = document.getElementById("sort-field");
    const runSortBtn = document.getElementById("run-sort-btn");
    const searchNameInput = document.getElementById("search-name-input");
    const runSearchBtn = document.getElementById("run-search-btn");
    const genReportBtn = document.getElementById("gen-report-btn");
    const algoOutputBox = document.getElementById("algo-output-box");
    const algoOutputContent = document.getElementById("algo-output-content");

    const aiNoteInput = document.getElementById("ai-note-input");
    const aiSummarizeBtn = document.getElementById("ai-summarize-btn");
    const aiSummaryOutput = document.getElementById("ai-summary-output");

    const aiSearchInput = document.getElementById("ai-search-input");
    const aiSearchBtn = document.getElementById("ai-search-btn");
    const aiSearchOutput = document.getElementById("ai-search-output");

    // ==========================================
    // ERROR HANDLING UTILITY
    // ==========================================
    function showError(message) {
        if (!errorBanner) return;
        errorBanner.textContent = message;
        errorBanner.classList.remove("hidden");
    }

    function hideError() {
        if (!errorBanner) return;
        errorBanner.textContent = "";
        errorBanner.classList.add("hidden");
    }

    // ==========================================
    // DOM CARD CREATION (document.createElement)
    // ==========================================
    function createStudentCard(student) {
        const card = document.createElement("article");
        card.className = "student-card";
        card.dataset.id = student.id;

        // Card Header
        const cardHeader = document.createElement("div");
        cardHeader.className = "card-header";

        const nameEl = document.createElement("h3");
        nameEl.className = "card-name";
        nameEl.textContent = student.name;

        const idEl = document.createElement("span");
        idEl.className = "card-id";
        idEl.textContent = `ID: #${student.id}`;

        cardHeader.appendChild(nameEl);
        cardHeader.appendChild(idEl);

        // Email
        const emailEl = document.createElement("p");
        emailEl.className = "card-email";
        emailEl.textContent = student.email;

        // Displayed Age Text
        const ageTextEl = document.createElement("p");
        ageTextEl.className = "card-age-text";
        ageTextEl.textContent = `Age: ${student.age}`;

        // Courses Count
        const coursesCount = student.courses ? student.courses.length : 0;
        const coursesEl = document.createElement("span");
        coursesEl.className = "card-courses";
        coursesEl.textContent = `📚 Enrolled Courses: ${coursesCount}`;

        // Inline Age Edit Controls
        const ageControlDiv = document.createElement("div");
        ageControlDiv.className = "card-age-control";

        const ageLabel = document.createElement("label");
        ageLabel.textContent = "New Age:";

        const ageInput = document.createElement("input");
        ageInput.type = "number";
        ageInput.className = "age-input";
        ageInput.value = student.age;
        ageInput.min = "1";

        const saveAgeBtn = document.createElement("button");
        saveAgeBtn.className = "btn btn-secondary btn-save-age";
        saveAgeBtn.textContent = "Save Age";
        saveAgeBtn.dataset.action = "save-age";

        ageControlDiv.appendChild(ageLabel);
        ageControlDiv.appendChild(ageInput);
        ageControlDiv.appendChild(saveAgeBtn);

        // Card Actions
        const cardActions = document.createElement("div");
        cardActions.className = "card-actions";

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-danger btn-delete";
        deleteBtn.textContent = "Delete Student";
        deleteBtn.dataset.action = "delete";

        cardActions.appendChild(deleteBtn);

        // Append all elements to card
        card.appendChild(cardHeader);
        card.appendChild(emailEl);
        card.appendChild(ageTextEl);
        card.appendChild(coursesEl);
        card.appendChild(ageControlDiv);
        card.appendChild(cardActions);

        return card;
    }

    // ==========================================
    // FETCH AND RENDER ROSTER
    // ==========================================
    async function fetchAndRenderRoster(minAge = null) {
        hideError();
        try {
            let url = `${BASE_URL}/students/`;
            if (minAge !== null && minAge !== "") {
                url += `?min_age=${encodeURIComponent(minAge)}`;
            }

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Failed to load student roster (HTTP status: ${response.status})`);
            }

            const students = await response.json();
            
            // Clear container and append cards
            rosterListContainer.innerHTML = "";
            students.forEach(student => {
                const card = createStudentCard(student);
                rosterListContainer.appendChild(card);
            });

            studentCountBadge.textContent = `${students.length} Students`;
        } catch (err) {
            showError("Could not reach the StudyTrack backend. Please ensure the FastAPI server is running.");
            console.error("Fetch Roster Error:", err);
        }
    }

    // ==========================================
    // EVENT DELEGATION ON #roster-list
    // ==========================================
    // Single event listener attached to container to handle "Save Age" and "Delete"
    rosterListContainer.addEventListener("click", async (event) => {
        const action = event.target.dataset.action;
        if (!action) return;

        const card = event.target.closest(".student-card");
        if (!card) return;
        const studentId = card.dataset.id;

        hideError();

        if (action === "save-age") {
            const ageInput = card.querySelector(".age-input");
            const newAge = parseInt(ageInput.value, 10);

            if (isNaN(newAge) || newAge <= 0) {
                showError("Age must be a valid positive integer.");
                return;
            }

            try {
                const response = await fetch(`${BASE_URL}/students/${studentId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ age: newAge })
                });

                if (!response.ok) {
                    const errData = await response.json().catch(() => ({}));
                    throw new Error(errData.detail || `Failed to update age (HTTP status: ${response.status})`);
                }

                const updatedStudent = await response.json();
                
                // Update displayed age text on card
                const ageTextEl = card.querySelector(".card-age-text");
                if (ageTextEl) {
                    ageTextEl.textContent = `Age: ${updatedStudent.age}`;
                }
            } catch (err) {
                showError(`Age update failed: ${err.message}`);
                console.error("Save Age Error:", err);
            }

        } else if (action === "delete") {
            try {
                const response = await fetch(`${BASE_URL}/students/${studentId}`, {
                    method: "DELETE"
                });

                if (!response.ok) {
                    throw new Error(`Failed to delete student (HTTP status: ${response.status})`);
                }

                // Remove card from DOM on success
                card.remove();
                
                // Update student count badge
                const currentCards = rosterListContainer.querySelectorAll(".student-card");
                studentCountBadge.textContent = `${currentCards.length} Students`;
            } catch (err) {
                showError(`Delete operation failed: ${err.message}`);
                console.error("Delete Student Error:", err);
            }
        }
    });

    // ==========================================
    // FORM SUBMIT HANDLER (ADD STUDENT)
    // ==========================================
    studentForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideError();

        const name = document.getElementById("student-name").value.trim();
        const email = document.getElementById("student-email").value.trim();
        const age = parseInt(document.getElementById("student-age").value, 10);

        if (!name || !email || isNaN(age)) {
            showError("Please fill out all student fields.");
            return;
        }

        try {
            const response = await fetch(`${BASE_URL}/students/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, age })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                let msg = errData.detail || `Server error (HTTP ${response.status})`;
                if (Array.isArray(errData.detail)) {
                    msg = errData.detail.map(d => d.msg).join("; ");
                }
                throw new Error(msg);
            }

            const newStudent = await response.json();
            
            // Create and append new card without full page reload
            const newCard = createStudentCard(newStudent);
            rosterListContainer.appendChild(newCard);

            // Update badge & reset form
            const currentCards = rosterListContainer.querySelectorAll(".student-card");
            studentCountBadge.textContent = `${currentCards.length} Students`;
            studentForm.reset();
        } catch (err) {
            showError(`Could not add student: ${err.message}`);
            console.error("Add Student Error:", err);
        }
    });

    // Filter Listeners
    applyFilterBtn.addEventListener("click", () => {
        const minAge = minAgeFilterInput.value;
        fetchAndRenderRoster(minAge);
    });

    clearFilterBtn.addEventListener("click", () => {
        minAgeFilterInput.value = "";
        fetchAndRenderRoster();
    });

    // ==========================================
    // ALGORITHMS ENGINE HANDLERS
    // ==========================================
    runSortBtn.addEventListener("click", async () => {
        hideError();
        const by = sortFieldSelect.value;
        try {
            const response = await fetch(`${BASE_URL}/students/sorted?by=${by}`);
            if (!response.ok) throw new Error("Failed to fetch sorted roster");
            const data = await response.json();
            
            algoOutputBox.classList.remove("hidden");
            algoOutputContent.textContent = `=== Insertion Sort (by ${by}) ===\n` + 
                JSON.stringify(data, null, 2);
        } catch (err) {
            showError(`Algorithm error: ${err.message}`);
        }
    });

    runSearchBtn.addEventListener("click", async () => {
        hideError();
        const name = searchNameInput.value.trim();
        if (!name) {
            showError("Please enter a name to search.");
            return;
        }
        try {
            const response = await fetch(`${BASE_URL}/students/search?name=${encodeURIComponent(name)}`);
            if (response.status === 404) {
                algoOutputBox.classList.remove("hidden");
                algoOutputContent.textContent = `=== Binary Search Result ===\nStudent '${name}' not found (404).`;
                return;
            }
            if (!response.ok) throw new Error("Search request failed");
            const data = await response.json();
            
            algoOutputBox.classList.remove("hidden");
            algoOutputContent.textContent = `=== Binary Search Result ===\nFound Record:\n` + 
                JSON.stringify(data, null, 2);
        } catch (err) {
            showError(`Search error: ${err.message}`);
        }
    });

    genReportBtn.addEventListener("click", async () => {
        hideError();
        try {
            const minAge = minAgeFilterInput.value || 21;
            const response = await fetch(`${BASE_URL}/students/report?min_age=${minAge}`);
            if (!response.ok) throw new Error("Failed to generate report");
            const data = await response.json();

            algoOutputBox.classList.remove("hidden");
            algoOutputContent.textContent = `=== Roster Report (Min Age: ${minAge}) ===\n` +
                `Count Meeting Min Age: ${data.count_meeting_min_age}\n\n` +
                `Report Text:\n${data.report}`;
        } catch (err) {
            showError(`Report error: ${err.message}`);
        }
    });

    // ==========================================
    // AI ASSISTANT HANDLERS
    // ==========================================
    aiSummarizeBtn.addEventListener("click", async () => {
        hideError();
        const text = aiNoteInput.value;
        try {
            const response = await fetch(`${BASE_URL}/assistant/summarize`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            if (!response.ok) throw new Error("Failed to summarize notes");
            const data = await response.json();

            aiSummaryOutput.classList.remove("hidden");
            aiSummaryOutput.innerHTML = `
                <h5>Topic: ${escapeHtml(data.topic)}</h5>
                <p><strong>Difficulty:</strong> <span class="badge">${data.difficulty}</span></p>
                <p style="margin-top: 8px;"><strong>Key Points:</strong></p>
                <ul>
                    ${data.key_points.length > 0 
                        ? data.key_points.map(kp => `<li>${escapeHtml(kp)}</li>`).join("") 
                        : "<li><em>(No key points extracted)</em></li>"}
                </ul>
            `;
        } catch (err) {
            showError(`AI Summarizer Error: ${err.message}`);
        }
    });

    aiSearchBtn.addEventListener("click", async () => {
        hideError();
        const query = aiSearchInput.value;
        try {
            const response = await fetch(`${BASE_URL}/assistant/search?query=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error("Failed to perform semantic note search");
            const results = await response.json();

            aiSearchOutput.classList.remove("hidden");
            if (results.length === 0) {
                aiSearchOutput.innerHTML = "<p>No matching notes found.</p>";
                return;
            }

            const itemsHtml = results.map(item => `
                <div class="ai-search-item">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>Note #${item.id}</strong>
                        <span class="score-badge">Score: ${item.score}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">${escapeHtml(item.text)}</p>
                </div>
            `).join("");

            aiSearchOutput.innerHTML = `<h5>Ranked Similarity Results:</h5>${itemsHtml}`;
        } catch (err) {
            showError(`AI Search Error: ${err.message}`);
        }
    });

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    // Initial Load
    fetchAndRenderRoster();
});
