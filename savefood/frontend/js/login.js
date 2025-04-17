document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const cancelBtn = document.getElementById("cancelBtn");
  const errorMessage = document.getElementById("errorMessage");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      errorMessage.textContent = "Please fill out both fields.";
      errorMessage.style.display = "block";
      return;
    }

    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed.");
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user_email", email);
      window.location.href = "/index.html"; // Redirect to homepage after login
    } catch (error) {
      errorMessage.textContent = error.message;
      errorMessage.style.display = "block";
    }
  });

  cancelBtn.addEventListener("click", () => {
    window.location.href = "/index.html";
  });
});
