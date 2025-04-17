// frontend/script.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("tagForm");
  const clearBtn = document.getElementById("clearBtn");
  const titleInput = document.getElementById("title");
  const descInput = document.getElementById("description");
  const tagsList = document.getElementById("tagsList");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = titleInput.value.trim();
    const description = descInput.value.trim();

    if (!title || !description) {
      tagsList.innerHTML = '<li class="error">Please fill in both fields</li>';
      return;
    }

    try {
      const response = await fetch(
        "http://localhost:8000/bags/tags/recommend",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, description }),
        }
      );
      if (!response.ok) throw new Error("Failed to fetch tags");
      const tags = await response.json();

      tagsList.innerHTML = "";
      tags.forEach((tag) => {
        const li = document.createElement("li");
        li.textContent = tag;
        tagsList.appendChild(li);
      });
    } catch (error) {
      tagsList.innerHTML = `<li class="error">Error: ${error.message}</li>`;
    }
  });

  clearBtn.addEventListener("click", () => {
    titleInput.value = "";
    descInput.value = "";
    tagsList.innerHTML = "";
  });
});
