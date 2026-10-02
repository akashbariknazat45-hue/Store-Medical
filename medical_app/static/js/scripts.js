/* =========================================
   MEDCARE JAVASCRIPT
========================================= */


document.addEventListener("DOMContentLoaded", function () {


    /* =====================================
       NAVBAR ACTIVE LINK
    ===================================== */

    const menuLinks =
        document.querySelectorAll(".menu-link");


    menuLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            menuLinks.forEach(function (item) {

                item.classList.remove("active");

            });

            link.classList.add("active");

        });

    });


    /* =====================================
       USER DROPDOWN
    ===================================== */

    const userButton =
        document.querySelector(".user-btn");

    const userMenu =
        document.querySelector(".user-menu");


    if (userButton && userMenu) {

        userButton.addEventListener("click", function (event) {

            event.stopPropagation();

            userMenu.classList.toggle("show");

        });


        document.addEventListener("click", function () {

            userMenu.classList.remove("show");

        });

    }


    /* =====================================
       SMOOTH SCROLL
    ===================================== */

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {

        link.addEventListener("click", function (event) {

            const target =
                document.querySelector(
                    link.getAttribute("href")
                );


            if (target) {

                event.preventDefault();

                target.scrollIntoView({

                    behavior: "smooth",

                    block: "start"

                });

            }

        });

    });


    /* =====================================
       BUTTON HOVER EFFECT
    ===================================== */

    const buttons =
        document.querySelectorAll(
            ".action-btn, .login-btn, .brand-icon"
        );


    buttons.forEach(function (button) {

        button.addEventListener("mouseenter", function () {

            button.style.transition =
                "all 0.25s ease";

        });

    });
    /* =====================================
    AI CHATBOT
    ===================================== */

    const aiChatButton =
        document.getElementById("aiChatButton");

    const aiChatWindow =
        document.getElementById("aiChatWindow");

    const aiCloseButton =
        document.getElementById("aiCloseButton");

    const aiMessageInput =
        document.getElementById("aiMessageInput");

    const aiSendButton =
        document.getElementById("aiSendButton");

    const aiChatMessages =
        document.getElementById("aiChatMessages");


    /* =====================================
    OPEN CHAT
    ===================================== */

    if (aiChatButton && aiChatWindow) {

        aiChatButton.addEventListener("click", function (event) {

            event.preventDefault();
            event.stopPropagation();

            aiChatWindow.classList.toggle("active");

        });

    }


    /* =====================================
    CLOSE CHAT
    ===================================== */

    if (aiCloseButton && aiChatWindow) {

        aiCloseButton.addEventListener("click", function (event) {

            event.preventDefault();

            aiChatWindow.classList.remove("active");

        });

    }


    /* =====================================
    SEND MESSAGE
    ===================================== */

    function sendAIMessage() {

        const message =
            aiMessageInput.value.trim();

        if (!message) {
            return;
        }


        /* User message */

        const userMessage =
            document.createElement("div");

        userMessage.className =
            "ai-message ai-user-message";

        userMessage.textContent =
            message;

        aiChatMessages.appendChild(
            userMessage
        );


        /* Clear input */

        aiMessageInput.value = "";


        /* Scroll */

        aiChatMessages.scrollTop =
            aiChatMessages.scrollHeight;


        /* AI loading */

        const loadingMessage =
            document.createElement("div");

        loadingMessage.className =
            "ai-message ai-bot-message";

        loadingMessage.textContent =
            "MedCare AI is thinking...";

        aiChatMessages.appendChild(
            loadingMessage
        );


        /* =====================================
        SEND TO DJANGO
        ===================================== */

        fetch("/ai-chat/", {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json",

                "X-CSRFToken":
                    getCookie("csrftoken")

            },

            body: JSON.stringify({

                message: message

            })

        })

        .then(function (response) {

            return response.json();

        })

        .then(function (data) {

        loadingMessage.remove();

        const botMessage =
            document.createElement("div");

        botMessage.className =
            "ai-message ai-bot-message";

        botMessage.textContent =
            data.reply ||
            data.message ||
            "Sorry, I could not understand.";

        aiChatMessages.appendChild(
            botMessage
        );

        aiChatMessages.scrollTop =
            aiChatMessages.scrollHeight;

        })

        .catch(function (error) {

        console.error("AI Error:", error);

        loadingMessage.textContent =
            "AI server error. Check Django terminal.";

        });

    }


    /* =====================================
    SEND BUTTON
    ===================================== */

    if (aiSendButton) {

        aiSendButton.addEventListener(
            "click",
            sendAIMessage
        );

    }


    /* =====================================
    ENTER KEY
    ===================================== */

    if (aiMessageInput) {

        aiMessageInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    sendAIMessage();

                }

            }
        );

    }


    /* =====================================
    CSRF COOKIE
    ===================================== */

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie &&
            document.cookie !== "") {

            const cookies =
                document.cookie.split(";");


            for (let cookie of cookies) {

                cookie = cookie.trim();


                if (
                    cookie.startsWith(
                        name + "="
                    )
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;

                }

            }

        }

        return cookieValue;

    }
    /* =========================================
    PRESCRIPTION UPLOAD
    ========================================= */

    const prescriptionButton =
        document.getElementById("aiPrescriptionButton");

    const prescriptionInput =
        document.getElementById("aiPrescriptionInput");


    if (prescriptionButton && prescriptionInput) {

        prescriptionButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                console.log("Prescription button clicked");

                prescriptionInput.click();

            }
        );


        prescriptionInput.addEventListener(
            "change",
            function () {

                const file = this.files[0];

                if (!file) {
                    return;
                }


                console.log(
                    "Prescription selected:",
                    file.name
                );


                /* File type */

                if (!file.type.startsWith("image/")) {

                    alert(
                        "Please select a prescription image."
                    );

                    this.value = "";

                    return;
                }


                /* File size */

                if (file.size > 10 * 1024 * 1024) {

                    alert(
                        "Image must be less than 10 MB."
                    );

                    this.value = "";

                    return;
                }


                /* Upload */

                uploadPrescription(file);

            }
        );

    }


    /* =========================================
    UPLOAD PRESCRIPTION
    ========================================= */

    async function uploadPrescription(file) {

        addAIMessage(
            "📷 Prescription uploaded. Please wait..."
        );


        const loadingMessage =
            addAILoading();


        const formData =
            new FormData();


        formData.append(
            "prescription",
            file
        );


        try {

            const response =
                await fetch(
                    "/ai-chat/",
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCookie("csrftoken")
                        },

                        body: formData
                    }
                );


            const data =
                await response.json();


            /* Remove loading */

            if (loadingMessage) {
                loadingMessage.remove();
            }


            /* Error */

            if (!response.ok) {

                addAIMessage(
                    data.error ||
                    "Unable to process prescription."
                );

                return;
            }


            /* AI reply */

            if (data.reply) {

                addAIMessage(
                    data.reply
                );

            }


            /* Products */

            if (
                data.products &&
                data.products.length > 0
            ) {

                showAIProducts(
                    data.products
                );

            }


            /* Clear file */

            prescriptionInput.value = "";


        } catch (error) {

            console.error(
                "Prescription Error:",
                error
            );


            if (loadingMessage) {
                loadingMessage.remove();
            }


            addAIMessage(
                "Unable to process the prescription. Please try again."
            );

        }

    }


    /* =========================================
    ADD AI MESSAGE
    ========================================= */

    function addAIMessage(message) {

        const messageBox =
            document.createElement("div");


        messageBox.className =
            "ai-message ai-bot-message";


        messageBox.innerHTML = `
            <div class="ai-message-icon">
                <i class="fa-solid fa-robot"></i>
            </div>

            <div class="ai-message-content">
                <p>${message}</p>
            </div>
        `;


        aiChatMessages.appendChild(
            messageBox
        );


        aiChatMessages.scrollTop =
            aiChatMessages.scrollHeight;

    }


    /* =========================================
    AI LOADING
    ========================================= */

    function addAILoading() {

        const loadingMessage =
            document.createElement("div");


        loadingMessage.className =
            "ai-message ai-bot-message";


        loadingMessage.innerHTML = `
            <div class="ai-message-icon">
                <i class="fa-solid fa-robot"></i>
            </div>

            <div class="ai-message-content">
                <p>MedCare AI is reading your prescription...</p>
            </div>
        `;


        aiChatMessages.appendChild(
            loadingMessage
        );


        aiChatMessages.scrollTop =
            aiChatMessages.scrollHeight;


        return loadingMessage;

    }


    /* =========================================
    SHOW PRODUCTS
    ========================================= */

    function showAIProducts(products) {

        let html = `
            <div class="ai-message ai-bot-message">

                <div class="ai-message-icon">
                    <i class="fa-solid fa-robot"></i>
                </div>

                <div class="ai-message-content">

                    <p>
                        💊 I found these products:
                    </p>

                    <div class="ai-product-list">
        `;


        products.forEach(function (product) {

            html += `
                <div class="ai-product-item">

                    <strong>
                        ${product.name}
                    </strong>

                    <div>
                        ₹${product.price}
                    </div>

                    <small>
                        Quantity: ${product.quantity}
                    </small>

                </div>
            `;

        });


        html += `
                    </div>

                    <p>
                        Would you like me to add these
                        medicines to your cart?
                    </p>

                    <button
                        type="button"
                        class="ai-confirm-cart-btn"
                        id="aiConfirmPrescription"
                    >
                        ✅ Yes, add them
                    </button>

                </div>

            </div>
        `;


        aiChatMessages.insertAdjacentHTML(
            "beforeend",
            html
        );


        aiChatMessages.scrollTop =
            aiChatMessages.scrollHeight;


        /* Confirmation button */

        const confirmButton =
            document.getElementById(
                "aiConfirmPrescription"
            );


        if (confirmButton) {

            confirmButton.addEventListener(
                "click",
                function () {

                    sendAIMessageText(
                        "Yes, add them"
                    );

                }
            );

        }

    }


    /* =========================================
    SEND CONFIRMATION MESSAGE
    ========================================= */

    function sendAIMessageText(message) {

        const loadingMessage =
            addAILoading();


        fetch("/ai-chat/", {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json",

                "X-CSRFToken":
                    getCookie("csrftoken")

            },

            body: JSON.stringify({

                message: message

            })

        })

        .then(function (response) {

            return response.json();

        })

        .then(function (data) {

            if (loadingMessage) {
                loadingMessage.remove();
            }


            addAIMessage(
                data.reply ||
                data.message ||
                "Done."
            );


            /* Update cart count if returned */

            if (data.cart_count !== undefined) {

                const cartCount =
                    document.getElementById(
                        "cartCount"
                    );


                if (cartCount) {

                    cartCount.textContent =
                        data.cart_count;

                }

            }

        })

        .catch(function (error) {

            console.error(
                "Confirmation error:",
                error
            );


            if (loadingMessage) {
                loadingMessage.remove();
            }


            addAIMessage(
                "Unable to add medicines to cart."
            );

        });

    }
    function showAIProducts(products) {

        const messages =
            document.getElementById("aiChatMessages");

        let html = `
            <div class="ai-message ai-bot-message">

                <div class="ai-message-icon">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="ai-message-content">
                    <p>
                        💊 I found these products:
                    </p>

                    <div class="ai-product-list">
        `;

        products.forEach(function (product) {

            html += `
                <div class="ai-product-item">

                    <div>
                        <strong>
                            ${product.name}
                        </strong>

                        <div>
                            ₹${product.price}
                        </div>

                        <small>
                            Quantity: ${product.quantity}
                        </small>
                    </div>

                </div>
            `;

        });

        html += `
                    </div>

                    <p>
                        Would you like me to add these
                        medicines to your cart?
                    </p>

                    <button
                        type="button"
                        class="ai-confirm-cart-btn"
                        onclick="sendAISuggestion('Yes, add them')"
                    >
                        ✅ Yes, add them
                    </button>

                </div>

            </div>
        `;

        messages.insertAdjacentHTML(
            "beforeend",
            html
        );

        messages.scrollTop =
            messages.scrollHeight;
    }
});