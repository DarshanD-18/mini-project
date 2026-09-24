document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       Load student
       ========================= */

    const savedUser =
        JSON.parse(
            localStorage.getItem("infoGainUser") || "null"
        );


    const studentName =
        document.getElementById("studentName");

    const profileName =
        document.getElementById("profileName");

    const profileUSN =
        document.getElementById("profileUSN");

    const avatar =
        document.getElementById("userAvatar");


    if (savedUser && savedUser.role === "student") {

        const name =
            savedUser.name || "Student";

        const usn =
            savedUser.usn ||
            savedUser.identifier ||
            "Not available";


        if (studentName) {
            studentName.textContent = name;
        }

        if (profileName) {
            profileName.textContent = name;
        }

        if (profileUSN) {
            profileUSN.textContent = usn;
        }

        if (avatar) {
            avatar.textContent =
                name.charAt(0).toUpperCase();
        }

    }


    /* =========================
       Mobile sidebar
       ========================= */

    const mobileMenu =
        document.getElementById("mobileMenu");

    const sidebar =
        document.getElementById("studentSidebar");


    if (mobileMenu && sidebar) {

        mobileMenu.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });

    }


    /* =========================
       Sidebar active state
       ========================= */

    const links =
        document.querySelectorAll(".side-link");


    links.forEach(link => {

        link.addEventListener("click", () => {

            links.forEach(item =>
                item.classList.remove("active")
            );

            link.classList.add("active");

            if (sidebar) {
                sidebar.classList.remove("open");
            }

        });

    });


    /* =========================
       Dashboard search
       ========================= */

    const dashboardSearch =
        document.getElementById("dashboardSearch");


    if (dashboardSearch) {

        dashboardSearch.addEventListener("keydown", event => {

            if (event.key !== "Enter") {
                return;
            }

            const query =
                dashboardSearch.value.trim();

            if (!query) {
                return;
            }

            const assistant =
                document.getElementById("assistant");

            const assistantInput =
                document.getElementById("assistantQuestion");

            if (assistant && assistantInput) {

                assistantInput.value = query;

                assistant.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });

                assistantInput.focus();

            }

        });

    }


    /* =========================
       Assistant demo
       ========================= */

    const assistantInput =
        document.getElementById("assistantQuestion");

    const askAssistant =
        document.getElementById("askAssistant");

    const assistantReply =
        document.getElementById("assistantReply");


    function answerQuestion() {

        if (!assistantInput || !assistantReply) {
            return;
        }

        const question =
            assistantInput.value.trim();

        if (!question) {

            assistantReply.textContent =
                "Please type a question first.";

            return;
        }


        assistantReply.textContent =
            `Demo response: I received your question about "${question}". The InfoGain chatbot API will be connected here later.`;

    }


    if (askAssistant) {
        askAssistant.addEventListener(
            "click",
            answerQuestion
        );
    }


    if (assistantInput) {

        assistantInput.addEventListener(
            "keydown",
            event => {

                if (event.key === "Enter") {
                    answerQuestion();
                }

            }
        );

    }


    /* =========================
       Demo action buttons
       ========================= */

    document
        .querySelectorAll(".quiz-button")
        .forEach(button => {

            button.addEventListener("click", () => {

                alert(
                    "Quiz module is ready for backend integration."
                );

            });

        });


    document
        .querySelectorAll(".subject-footer button")
        .forEach(button => {

            button.addEventListener("click", () => {

                alert(
                    "Subject progress module will load detailed topics here."
                );

            });

        });


    document
        .querySelectorAll(".question-row button")
        .forEach(button => {

            button.addEventListener("click", () => {

                alert(
                    "PYQ viewer will open here after the PYQ backend is connected."
                );

            });

        });


    /* =========================
       Logout
       ========================= */

    const logout =
        document.getElementById("studentLogout");


    if (logout) {

        logout.addEventListener("click", () => {

            localStorage.removeItem("infoGainUser");
            sessionStorage.removeItem("infoGainSession");

            window.location.href = "/";

        });

    }

});