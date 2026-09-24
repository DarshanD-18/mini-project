document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       Helpers
       ========================= */

    function showMessage(element, message, type) {
        if (!element) return;

        element.textContent = message;
        element.className = `form-message ${type}`;
    }


    function saveUser(user) {
        localStorage.setItem("infoGainUser", JSON.stringify(user));
    }


    /* =========================
       Student password toggle
       ========================= */

    const studentPassword =
        document.getElementById("studentPassword");

    const toggleStudentPassword =
        document.getElementById("toggleStudentPassword");

    if (studentPassword && toggleStudentPassword) {

        toggleStudentPassword.addEventListener("click", () => {

            const visible =
                studentPassword.type === "text";

            studentPassword.type =
                visible ? "password" : "text";

            toggleStudentPassword.textContent =
                visible ? "Show" : "Hide";

        });

    }


    /* =========================
       Admin password toggle
       ========================= */

    const adminPassword =
        document.getElementById("adminPassword");

    const toggleAdminPassword =
        document.getElementById("toggleAdminPassword");

    if (adminPassword && toggleAdminPassword) {

        toggleAdminPassword.addEventListener("click", () => {

            const visible =
                adminPassword.type === "text";

            adminPassword.type =
                visible ? "password" : "text";

            toggleAdminPassword.textContent =
                visible ? "Show" : "Hide";

        });

    }


    /* =========================
       Student Login
       ========================= */

    const studentLoginForm =
        document.getElementById("studentLoginForm");

    if (studentLoginForm) {

        studentLoginForm.addEventListener("submit", (event) => {

            event.preventDefault();

            const identifier =
                document.getElementById("studentIdentifier")
                    .value
                    .trim();

            const password =
                document.getElementById("studentPassword")
                    .value
                    .trim();

            const remember =
                document.getElementById("rememberStudent")
                    .checked;

            const message =
                document.getElementById("loginMessage");


            if (!identifier || !password) {

                showMessage(
                    message,
                    "Please enter your login details.",
                    "error"
                );

                return;
            }


            const user = {

                role: "student",

                name: "Darshan",

                identifier: identifier,

                usn: identifier,

                email:
                    identifier.includes("@")
                        ? identifier
                        : `${identifier.toLowerCase()}@college.edu`,

                loginTime:
                    new Date().toISOString()

            };


            saveUser(user);


            if (remember) {
                localStorage.setItem(
                    "infoGainRememberMe",
                    "true"
                );
            } else {
                sessionStorage.setItem(
                    "infoGainSession",
                    "student"
                );
            }


            showMessage(
                message,
                "Login successful. Opening your dashboard...",
                "success"
            );


            setTimeout(() => {

                window.location.href =
                    "/student/dashboard";

            }, 700);

        });

    }


    /* =========================
       Student Registration
       ========================= */

    const showRegister =
        document.getElementById("showRegister");

    const registerForm =
        document.getElementById("studentRegisterForm");

    const backToLogin =
        document.getElementById("backToLogin");

    const loginForm =
        document.getElementById("studentLoginForm");


    if (showRegister && registerForm) {

        showRegister.addEventListener("click", () => {

            registerForm.classList.remove("hidden");

            showRegister.classList.add("hidden");

            if (loginForm) {
                loginForm.classList.add("hidden");
            }

        });

    }


    if (backToLogin) {

        backToLogin.addEventListener("click", () => {

            registerForm.classList.add("hidden");

            showRegister.classList.remove("hidden");

            if (loginForm) {
                loginForm.classList.remove("hidden");
            }

        });

    }


    if (registerForm) {

        registerForm.addEventListener("submit", (event) => {

            event.preventDefault();

            const name =
                document.getElementById("registerName")
                    .value
                    .trim();

            const usn =
                document.getElementById("registerUSN")
                    .value
                    .trim();

            const email =
                document.getElementById("registerEmail")
                    .value
                    .trim();

            const password =
                document.getElementById("registerPassword")
                    .value
                    .trim();

            const message =
                document.getElementById("registerMessage");


            if (!name || !usn || !email || !password) {

                showMessage(
                    message,
                    "Please fill in all fields.",
                    "error"
                );

                return;
            }


            const users =
                JSON.parse(
                    localStorage.getItem("infoGainStudents") || "[]"
                );


            const existing =
                users.find(
                    user =>
                        user.usn.toLowerCase() === usn.toLowerCase() ||
                        user.email.toLowerCase() === email.toLowerCase()
                );


            if (existing) {

                showMessage(
                    message,
                    "An account with this USN or email already exists.",
                    "error"
                );

                return;
            }


            users.push({

                name,
                usn,
                email,
                password

            });


            localStorage.setItem(
                "infoGainStudents",
                JSON.stringify(users)
            );


            showMessage(
                message,
                "Account created. You can now sign in.",
                "success"
            );


            setTimeout(() => {

                registerForm.classList.add("hidden");

                showRegister.classList.remove("hidden");

                if (loginForm) {
                    loginForm.classList.remove("hidden");
                }

                document.getElementById(
                    "studentIdentifier"
                ).value = usn;

            }, 900);

        });

    }


    /* =========================
       Admin Login
       ========================= */

    const adminLoginForm =
        document.getElementById("adminLoginForm");


    if (adminLoginForm) {

        adminLoginForm.addEventListener("submit", (event) => {

            event.preventDefault();

            const identifier =
                document.getElementById("adminIdentifier")
                    .value
                    .trim();

            const password =
                document.getElementById("adminPassword")
                    .value
                    .trim();

            const message =
                document.getElementById("adminLoginMessage");


            if (!identifier || !password) {

                showMessage(
                    message,
                    "Please enter your staff login details.",
                    "error"
                );

                return;
            }


            const admin = {

                role: "admin",

                name: "Admin Staff",

                identifier,

                loginTime:
                    new Date().toISOString()

            };


            saveUser(admin);


            showMessage(
                message,
                "Access verified. Opening admin portal...",
                "success"
            );


            setTimeout(() => {

                window.location.href =
                    "/admin/dashboard";

            }, 700);

        });

    }


    /* =========================
       Forgot password
       ========================= */

    const forgotPassword =
        document.getElementById("forgotPassword");

    if (forgotPassword) {

        forgotPassword.addEventListener("click", (event) => {

            event.preventDefault();

            alert(
                "Password recovery will be connected to the backend authentication system."
            );

        });

    }


    const adminForgotPassword =
        document.getElementById("adminForgotPassword");

    if (adminForgotPassword) {

        adminForgotPassword.addEventListener("click", (event) => {

            event.preventDefault();

            alert(
                "Admin password recovery will be handled by the secure backend authentication system."
            );

        });

    }

});