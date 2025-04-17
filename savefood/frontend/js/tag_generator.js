document.addEventListener("DOMContentLoaded", () => {
  const tagForm = document.getElementById("tagForm");
  const clearBtn = document.getElementById("clearBtn");
  const tagsList = document.getElementById("tagsList");

  tagForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("bagTitle").value.trim();
    const description = document.getElementById("bagDescription").value.trim();

    if (!title || !description) {
      alert("Please fill out both fields.");
      return;
    }

    console.log("Sending tag recommendation request:", { title, description });
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/bags/tags/recommend",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ title, description }),
        }
      );

      console.log("Tag recommendation response status:", response.status);
      const tags = await response.json();
      console.log("Recommended tags:", tags);

      if (!response.ok) {
        throw new Error(tags.detail || "Failed to generate tags.");
      }

      // Display the tags
      tagsList.innerHTML = "";
      if (tags.length === 0) {
        tagsList.innerHTML = "<li>No tags recommended.</li>";
      } else {
        tags.forEach((tag) => {
          const li = document.createElement("li");
          li.textContent = tag;
          tagsList.appendChild(li);
        });
      }
    } catch (error) {
      console.error("Tag generation error:", error.message);
      tagsList.innerHTML = `<li class="error">Error: ${error.message}</li>`;
    }
  });

  clearBtn.addEventListener("click", () => {
    document.getElementById("bagTitle").value = "";
    document.getElementById("bagDescription").value = "";
    tagsList.innerHTML = "";
    console.log("Form cleared");
  });
});
