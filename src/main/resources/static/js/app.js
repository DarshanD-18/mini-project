/* =========================================================
   INFOGAIN
   STUDENT INFORMATION PORTAL
========================================================= */


document.addEventListener("DOMContentLoaded", () => {


    /* =====================================================
       ELEMENTS
    ===================================================== */

    const questionForm =
        document.getElementById("questionForm");

    const questionInput =
        document.getElementById("questionInput");

    const popularLinks =
        document.querySelectorAll(".popular-link");

    const questionCards =
        document.querySelectorAll(".question-card");

    const serviceCards =
        document.querySelectorAll(".service-card");

    const topicItems =
        document.querySelectorAll(".topic-item");

    const faqItems =
        document.querySelectorAll(".faq-item");

    const navLinks =
        document.querySelectorAll(".nav-link");

    const mainNav =
        document.getElementById("mainNav");

    const mobileMenuButton =
        document.getElementById("mobileMenuButton");

    const questionModal =
        document.getElementById("questionModal");

    const modalClose =
        document.getElementById("modalClose");

    const modalCancel =
        document.getElementById("modalCancel");

    const modalQuestionText =
        document.getElementById("modalQuestionText");

    const currentYear =
        document.getElementById("currentYear");


    /* =====================================================
       YEAR
    ===================================================== */

    if (currentYear) {

        currentYear.textContent =
            new Date().getFullYear();

    }


    /* =====================================================
       SET QUESTION
    ===================================================== */

    function setQuestion(question) {

        if (
            !questionInput ||
            !question
        ) {

            return;

        }


        questionInput.value =
            question;


        questionInput.focus();


        questionInput.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    }


    /* =====================================================
       POPULAR LINKS
    ===================================================== */

    popularLinks.forEach(
        (button) => {

            button.addEventListener(
                "click",
                () => {

                    const question =
                        button.dataset.question;

                    setQuestion(
                        question
                    );

                }
            );

        }
    );


    /* =====================================================
       QUESTION CARDS
    ===================================================== */

    questionCards.forEach(
        (card) => {

            card.addEventListener(
                "click",
                () => {

                    const question =
                        card.dataset.question;

                    setQuestion(
                        question
                    );

                }
            );

        }
    );


    /* =====================================================
       SERVICE CARDS
    ===================================================== */

    serviceCards.forEach(
        (card) => {

            card.addEventListener(
                "click",
                () => {

                    const question =
                        card.dataset.question;

                    setQuestion(
                        question
                    );

                }
            );

        }
    );


    /* =====================================================
       TOPIC ITEMS
    ===================================================== */

    topicItems.forEach(
        (item) => {

            item.addEventListener(
                "click",
                () => {

                    const question =
                        item.dataset.question;

                    setQuestion(
                        question
                    );

                }
            );

        }
    );


    /* =====================================================
       MAIN SEARCH FORM
    ===================================================== */

    if (questionForm) {

        questionForm.addEventListener(
            "submit",
            (event) => {

                event.preventDefault();


                const question =
                    questionInput.value.trim();


                if (!question) {

                    questionInput.focus();


                    questionInput.classList.add(
                        "empty-input"
                    );


                    setTimeout(
                        () => {

                            questionInput.classList.remove(
                                "empty-input"
                            );

                        },
                        500
                    );


                    return;

                }


                openQuestionModal(
                    question
                );

            }
        );

    }


    /* =====================================================
       QUESTION MODAL
    ===================================================== */

    function openQuestionModal(question) {

        if (!questionModal) {

            return;

        }


        if (modalQuestionText) {

            modalQuestionText.textContent =
                `"${question}"`;

        }


        questionModal.classList.add(
            "show"
        );


        document.body.classList.add(
            "modal-open"
        );


        sessionStorage.setItem(
            "pendingQuestion",
            question
        );

    }


    function closeQuestionModal() {

        if (!questionModal) {

            return;

        }


        questionModal.classList.remove(
            "show"
        );


        document.body.classList.remove(
            "modal-open"
        );

    }


    if (modalClose) {

        modalClose.addEventListener(
            "click",
            closeQuestionModal
        );

    }


    if (modalCancel) {

        modalCancel.addEventListener(
            "click",
            closeQuestionModal
        );

    }


    if (questionModal) {

        questionModal.addEventListener(
            "click",
            (event) => {

                if (
                    event.target ===
                    questionModal
                ) {

                    closeQuestionModal();

                }

            }
        );

    }


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key ===
                "Escape"
            ) {

                closeQuestionModal();

            }

        }
    );


    /* =====================================================
       MOBILE NAVIGATION
    ===================================================== */

    if (
        mobileMenuButton &&
        mainNav
    ) {

        mobileMenuButton.addEventListener(
            "click",
            () => {

                mainNav.classList.toggle(
                    "open"
                );

            }
        );

    }


    /* =====================================================
       CLOSE MOBILE NAVIGATION
    ===================================================== */

    navLinks.forEach(
        (link) => {

            link.addEventListener(
                "click",
                () => {

                    if (mainNav) {

                        mainNav.classList.remove(
                            "open"
                        );

                    }

                }
            );

        }
    );


    document.addEventListener(
        "click",
        (event) => {

            if (
                !mainNav ||
                !mobileMenuButton
            ) {

                return;

            }


            const insideMenu =
                mainNav.contains(
                    event.target
                );


            const insideButton =
                mobileMenuButton.contains(
                    event.target
                );


            if (
                !insideMenu &&
                !insideButton
            ) {

                mainNav.classList.remove(
                    "open"
                );

            }

        }
    );


    /* =====================================================
       ACTIVE NAVIGATION
    ===================================================== */

    const navigationSections = [

        document.getElementById("home"),

        document.getElementById("services"),

        document.getElementById("topics"),

        document.getElementById("how-it-works")

    ].filter(Boolean);


    function updateNavigation() {

        const position =
            window.scrollY + 150;


        let current =
            "home";


        navigationSections.forEach(
            (section) => {

                if (
                    position >=
                    section.offsetTop
                ) {

                    current =
                        section.id;

                }

            }
        );


        navLinks.forEach(
            (link) => {

                const href =
                    link.getAttribute(
                        "href"
                    );


                if (
                    href ===
                    `#${current}`
                ) {

                    link.classList.add(
                        "active"
                    );

                } else {

                    link.classList.remove(
                        "active"
                    );

                }

            }
        );

    }


    window.addEventListener(
        "scroll",
        updateNavigation,
        {
            passive: true
        }
    );


    updateNavigation();


    /* =====================================================
       FAQ ACCORDION
    ===================================================== */

    faqItems.forEach(
        (item) => {

            const button =
                item.querySelector(
                    ".faq-question"
                );

            const answer =
                item.querySelector(
                    ".faq-answer"
                );


            if (
                !button ||
                !answer
            ) {

                return;

            }


            button.addEventListener(
                "click",
                () => {

                    const currentlyOpen =
                        item.classList.contains(
                            "active"
                        );


                    /* CLOSE ALL */

                    faqItems.forEach(
                        (otherItem) => {

                            otherItem.classList.remove(
                                "active"
                            );


                            const otherAnswer =
                                otherItem.querySelector(
                                    ".faq-answer"
                                );


                            if (
                                otherAnswer
                            ) {

                                otherAnswer.style.maxHeight =
                                    null;

                            }

                        }
                    );


                    /* OPEN SELECTED */

                    if (!currentlyOpen) {

                        item.classList.add(
                            "active"
                        );


                        answer.style.maxHeight =
                            answer.scrollHeight +
                            "px";

                    }

                }
            );

        }
    );


    /* =====================================================
       FAQ RESIZE
    ===================================================== */

    window.addEventListener(
        "resize",
        () => {

            const openedAnswer =
                document.querySelector(
                    ".faq-item.active .faq-answer"
                );


            if (openedAnswer) {

                openedAnswer.style.maxHeight =
                    openedAnswer.scrollHeight +
                    "px";

            }

        }
    );


    /* =====================================================
       PENDING QUESTION
    ===================================================== */

    const pendingQuestion =
        sessionStorage.getItem(
            "pendingQuestion"
        );


    if (
        pendingQuestion &&
        questionInput
    ) {

        questionInput.dataset.pendingQuestion =
            pendingQuestion;

    }


    /* =====================================================
       INFOGAIN API STRUCTURE
       These endpoints will be connected to Spring Boot.
    ===================================================== */

    window.InfoGain = {

        API: {

            chat:
                "/api/chat",

            login:
                "/api/auth/login",

            register:
                "/api/auth/register",

            studentProfile:
                "/api/student/profile",

            studentHistory:
                "/api/student/history",

            adminDashboard:
                "/api/admin/dashboard",

            adminStudents:
                "/api/admin/students",

            adminFaqs:
                "/api/admin/faqs",

            adminDocuments:
                "/api/admin/documents",

            adminNotices:
                "/api/admin/notices",

            adminAnalytics:
                "/api/admin/analytics"

        },


        getPendingQuestion() {

            return sessionStorage.getItem(
                "pendingQuestion"
            );

        },


        setPendingQuestion(question) {

            sessionStorage.setItem(
                "pendingQuestion",
                question
            );

        },


        clearPendingQuestion() {

            sessionStorage.removeItem(
                "pendingQuestion"
            );

        }

    };


    /* =====================================================
       INPUT RESET
    ===================================================== */

    if (questionInput) {

        questionInput.addEventListener(
            "input",
            () => {

                questionInput.classList.remove(
                    "empty-input"
                );

            }
        );

    }


    /* =====================================================
       CARD REVEAL
    ===================================================== */

    const revealElements =
        document.querySelectorAll(
            ".question-card, .service-card, .topic-item"
        );


    if (
        "IntersectionObserver" in window
    ) {

        const revealObserver =
            new IntersectionObserver(
                (
                    entries,
                    observer
                ) => {

                    entries.forEach(
                        (entry) => {

                            if (
                                !entry.isIntersecting
                            ) {

                                return;

                            }


                            entry.target.classList.add(
                                "visible"
                            );


                            observer.unobserve(
                                entry.target
                            );

                        }
                    );

                },
                {
                    threshold: 0.08
                }
            );


        revealElements.forEach(
            (element) => {

                element.classList.add(
                    "reveal-item"
                );


                revealObserver.observe(
                    element
                );

            }
        );

    } else {

        revealElements.forEach(
            (element) => {

                element.classList.add(
                    "visible"
                );

            }
        );

    }


});