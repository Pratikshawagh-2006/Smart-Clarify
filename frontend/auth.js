const API_BASE = "http://127.0.0.1:8000";

// ROLE and ROLE_LABEL are defined in each HTML file before this script loads

function showMessage(el, text, type) {
    el.textContent = text;
    el.className = "message " + type;
}

function hideMessage(el) {
    el.className = "message";
}

function switchTab(tab) {
    document.getElementById("login-tab-btn").classList.toggle("active", tab === "login");
    document.getElementById("register-tab-btn").classList.toggle("active", tab === "register");
    document.getElementById("login-form").classList.toggle("hidden", tab !== "login");
    document.getElementById("register-form").classList.toggle("hidden", tab !== "register");
    document.getElementById("otp-form").classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("role-label").textContent = ROLE_LABEL;

    document.getElementById("login-tab-btn").addEventListener("click", () => switchTab("login"));
    document.getElementById("register-tab-btn").addEventListener("click", () => switchTab("register"));

    // ---------------- LOGIN ----------------
    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = document.getElementById("login-message");
        hideMessage(msg);

        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value.trim();

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (!res.ok) {
                showMessage(msg, data.detail || "Login failed", "error");
                return;
            }

            if (data.role !== ROLE) {
                showMessage(msg, `Yeh account "${data.role}" hai — is portal (${ROLE}) se login mat karo.`, "error");
                return;
            }

            localStorage.setItem("sc_token", data.access_token);
            localStorage.setItem("sc_role", data.role);
            localStorage.setItem("sc_id", data.id);
            localStorage.setItem("sc_email", email);

            showMessage(msg, `Login successful! Logged in as ${data.role} (ID: ${data.id}).`, "success");

            setTimeout(() => {
                window.location.href = `${ROLE}-dashboard.html`;
            }, 600);

        } catch (err) {
            showMessage(msg, "Backend se connect nahi ho paaya — check karo uvicorn chal raha hai ya nahi.", "error");
        }
    });

    // ---------------- REGISTER ----------------
    document.getElementById("register-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = document.getElementById("register-message");
        hideMessage(msg);

        const name = document.getElementById("reg-name").value.trim();
        const email = document.getElementById("reg-email").value.trim();
        const password = document.getElementById("reg-password").value.trim();

        if (!name || !email || !password) {
            showMessage(msg, "Saare fields bharo.", "error");
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password, role: ROLE })
            });
            const data = await res.json();

            if (!res.ok) {
                showMessage(msg, data.detail || "Registration failed", "error");
                return;
            }

            showMessage(msg, "OTP tumhare email pe bhej diya gaya hai.", "success");

            document.getElementById("register-form").classList.add("hidden");
            document.getElementById("otp-form").classList.remove("hidden");
            document.getElementById("otp-email").value = email;

        } catch (err) {
            showMessage(msg, "Backend se connect nahi ho paaya.", "error");
        }
    });

    // ---------------- VERIFY OTP ----------------
    document.getElementById("otp-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = document.getElementById("otp-message");
        hideMessage(msg);

        const email = document.getElementById("otp-email").value;
        const otp = document.getElementById("otp-code").value.trim();

        try {
            const res = await fetch(`${API_BASE}/auth/verify-otp`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, otp })
            });
            const data = await res.json();

            if (!res.ok) {
                showMessage(msg, data.detail || "Verification failed", "error");
                return;
            }

            showMessage(msg, "Email verified! Ab login tab se login kar sakte ho.", "success");

            setTimeout(() => {
                document.getElementById("otp-form").classList.add("hidden");
                switchTab("login");
            }, 1500);

        } catch (err) {
            showMessage(msg, "Backend se connect nahi ho paaya.", "error");
        }
    });

    // ---------------- RESEND OTP ----------------
    document.getElementById("resend-otp-btn").addEventListener("click", async () => {
        const msg = document.getElementById("otp-message");
        const email = document.getElementById("otp-email").value;

        try {
            const res = await fetch(`${API_BASE}/auth/resend-otp`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            showMessage(msg, data.message || data.detail || "Resend attempted", res.ok ? "success" : "error");
        } catch (err) {
            showMessage(msg, "Backend se connect nahi ho paaya.", "error");
        }
    });
});