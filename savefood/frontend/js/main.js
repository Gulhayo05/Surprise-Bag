document.addEventListener("DOMContentLoaded", () => {
  console.log("main.js loaded successfully at", new Date().toISOString());

  const loginBtn = document.getElementById("loginBtn");
  if (!loginBtn) {
    console.error(
      'Login button not found. Ensure the element with id="loginBtn" exists in the HTML.'
    );
    return;
  }
  console.log("Login button found:", loginBtn);

  // Check if user is logged in
  const token = localStorage.getItem("access_token");
  const userEmail = localStorage.getItem("user_email");
  if (token && userEmail) {
    console.log("User is logged in:", userEmail);
    loginBtn.textContent = `Logout (${userEmail})`;
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_email");
      console.log("User logged out");
      window.location.reload();
    });
  } else {
    console.log("User is not logged in");
    loginBtn.textContent = "Login";
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      console.log("Login button clicked");
      showLoginModal();
    });
  }

  function showLoginModal() {
    console.log("Showing login modal");
    const modal = document.createElement("div");
    modal.className = "login-modal";
    modal.innerHTML = `
            <div class="modal-content">
                <h2>Login to Surprise Bag</h2>
                <form id="loginForm">
                    <div class="input-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" placeholder="e.g., user@example.com" required>
                    </div>
                    <div class="input-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" placeholder="Enter your password" required>
                    </div>
                    <div class="button-group">
                        <button type="submit" class="generate-btn">Login</button>
                        <button type="button" class="clear-btn" id="cancelBtn">Cancel</button>
                    </div>
                </form>
                <p id="errorMessage" class="error" style="display: none;"></p>
            </div>
        `;
    document.body.appendChild(modal);

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

      console.log("Sending login request:", { email, password });

      // Prepare form data to match OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append("username", email); // Backend expects 'username' as email
      formData.append("password", password);

      try {
        const response = await fetch("http://127.0.0.1:8000/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: formData,
        });

        console.log("Login response status:", response.status);
        const data = await response.json();
        console.log("Login response data:", data);

        if (!response.ok) {
          throw new Error(data.detail || "Login failed.");
        }

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_email", email);
        console.log("Token stored:", data.access_token);
        modal.remove();
        window.location.reload();
      } catch (error) {
        console.error("Login error:", error.message);
        errorMessage.textContent = error.message;
        errorMessage.style.display = "block";
      }
    });

    cancelBtn.addEventListener("click", () => {
      console.log("Login modal cancelled");
      modal.remove();
    });
  }
});
