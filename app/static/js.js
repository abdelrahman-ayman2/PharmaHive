const buttons = document.querySelectorAll(".show-password");

buttons.forEach((e) => {
    e.addEventListener("click", showpassword);
})

function showpassword() {
    let pass1 = document.getElementById("password");
    let pass2 = document.getElementById("confirm_password");
    let pass3 = document.getElementById("new_password");

    if (pass1.type === "password") {
        pass1.type = "text";
        pass2.type = "text";
        pass3.type = "text";
    } else {
        pass1.type = "password";
        pass2.type = "password";
        pass3.type = "password";
    }
}

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", function(e) {
        let password = document.getElementById("password").value;
        let confirm = document.getElementById("confirm_password").value;

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
            if (length > 280 || length === 0) {
                btn.disabled = true;
            } else {
                btn.disabled = false;
            }
        }
    });
});