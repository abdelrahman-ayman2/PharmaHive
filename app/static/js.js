const buttons = document.querySelectorAll(".show-password");

buttons.forEach((button) => {
    button.addEventListener("click", showpassword);
});

function showpassword() {
    const pass1 = document.getElementById("password");
    const pass2 = document.getElementById("confirm_password");
    const pass3 = document.getElementById("new_password");

    const passwordFields = [pass1, pass2, pass3].filter(Boolean);

    if (!passwordFields.length) return;

    const isPasswordType = passwordFields[0].type === "password";

    passwordFields.forEach((field) => {
        field.type = isPasswordType ? "text" : "password";
    });
}

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
        const passwordInput = document.getElementById("password");
        const confirmInput = document.getElementById("confirm_password");

        if (!passwordInput || !confirmInput) return;

        const password = passwordInput.value;
        const confirm = confirmInput.value;

        if (password !== confirm) {
            e.preventDefault();
            alert("Passwords do not match");
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const deleteBtn = document.getElementById("delete-btn");
    const deleteForm = document.getElementById("delete-form");
    const cancelDelete = document.getElementById("cancel-delete");

    if (deleteBtn && deleteForm) {
        deleteBtn.addEventListener("click", function () {
            deleteForm.classList.remove("d-none");
            deleteBtn.classList.add("d-none");
        });
    }

    if (cancelDelete && deleteForm && deleteBtn) {
        cancelDelete.addEventListener("click", function () {
            deleteForm.classList.add("d-none");
            deleteBtn.classList.remove("d-none");
        });
    }
});

const textareas = document.querySelectorAll(".textarea");
const counters = document.querySelectorAll(".char-counter");
const btn = document.getElementById("postBtn");

textareas.forEach((textarea, index) => {
    const counter = counters[index];

    if (!textarea || !counter) return;

    textarea.addEventListener("input", function () {
        const length = textarea.value.length;

        counter.textContent = `${length} / 280`;
        counter.classList.remove("warning", "danger");

        if (length > 240) {
            counter.classList.add("warning");
        }

        if (length >= 280) {
            counter.classList.add("danger");
        }

        if (btn) {
            btn.disabled = length > 280 || length === 0;
        }
    });
});

const likes = document.querySelectorAll(".like_update");
const csrfMeta = document.querySelector('meta[name="csrf-token"]');
const csrfToken = csrfMeta ? csrfMeta.getAttribute("content") : null;

if (likes.length && csrfToken) {
    likes.forEach((button) => {
        button.addEventListener("click", like_update);
    });
}

function like_update(event) {
    if (!csrfToken) return;

    const button = event.currentTarget;
    const postId = button.dataset.postId;

    button.disabled = true;

    fetch(`/posts/${postId}/like`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then((res) => res.json())
    .then((data) => {
        const likesCount = document.getElementById(`likes-${postId}`);
        if (likesCount) {
            likesCount.innerText = data.likes_count;
        }
    })
    .finally(() => {
        button.disabled = false;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const otpInputs = document.querySelectorAll(".otp-input");
    const otpHidden = document.getElementById("otp");

    if (!otpInputs.length || !otpHidden) return;

    otpInputs.forEach((input, index) => {
        input.addEventListener("input", (e) => {
            let value = e.target.value.replace(/[^0-9]/g, "");
            e.target.value = value.slice(0, 1);

            if (e.target.value !== "" && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }

            otpHidden.value = Array.from(otpInputs).map((inp) => inp.value).join("");
        });

        input.addEventListener("keydown", (e) => {
            if (e.key === "Backspace" && input.value === "" && index > 0) {
                otpInputs[index - 1].focus();
            }
        });

        input.addEventListener("paste", (e) => {
            e.preventDefault();

            const pasted = (e.clipboardData || window.clipboardData)
                .getData("text")
                .replace(/[^0-9]/g, "")
                .slice(0, otpInputs.length);

            if (!pasted) return;

            pasted.split("").forEach((char, i) => {
                if (otpInputs[i]) {
                    otpInputs[i].value = char;
                }
            });

            otpHidden.value = Array.from(otpInputs).map((inp) => inp.value).join("");

            const nextIndex = Math.min(pasted.length, otpInputs.length - 1);
            otpInputs[nextIndex].focus();
        });
    });

    otpInputs[0].focus();
});