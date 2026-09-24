document.addEventListener("DOMContentLoaded", () => {

    /* =========================
       Mobile menu
       ========================= */

    const menu =
        document.getElementById("adminMenu");

    const sidebar =
        document.getElementById("adminSidebar");


    if (menu && sidebar) {

        menu.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });

    }


    /* =========================
       Navigation
       ========================= */

    const links =
        document.querySelectorAll(".admin-link");


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
       Management buttons
       ========================= */

    document
        .querySelectorAll(".management-card button")
        .forEach(button => {

            button.addEventListener("click", () => {

                const card =
                    button.closest(".management-card");

                const title =
                    card?.querySelector("h3")?.textContent ||
                    "Management module";

                alert(
                    `${title} is ready for backend integration.`
                );

            });

        });


    /* =========================
       Question review buttons
       ========================= */

    document
        .querySelectorAll(".query-item button")
        .forEach(button => {

            button.addEventListener("click", () => {

                alert(
                    "Question review module will open here."
                );

            });

        });


    /* =========================
       Notice publishing
       ========================= */

    const noticeForm =
        document.getElementById("noticeForm");

    const noticeMessage =
        document.getElementById("noticeMessage");


    if (noticeForm) {

        noticeForm.addEventListener("submit", event => {

            event.preventDefault();

            const title =
                document.getElementById("noticeTitle")
                    .value
                    .trim();

            const text =
                document.getElementById("noticeText")
                    .value
                    .trim();


            if (!title || !text) {
                return;
            }


            noticeMessage.textContent =
                "Notice prepared successfully. Backend publishing will be connected later.";

            noticeForm.reset();

        });

    }


    /* =========================
       Logout
       ========================= */

    const logout =
        document.getElementById("adminLogout");


    if (logout) {

        logout.addEventListener("click", () => {

            localStorage.removeItem("infoGainUser");

            window.location.href = "/";

        });

    }


});