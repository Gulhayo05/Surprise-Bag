document.addEventListener("DOMContentLoaded", () => {
  fetchBags();
});

async function fetchBags(maxRetries = 3) {
  const bagsList = document.getElementById("bagsList");
  bagsList.innerHTML = "<p>Loading...</p>";

  let attempts = 0;
  while (attempts < maxRetries) {
    try {
      const response = await fetch("/bags/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const bags = await response.json();
      console.log("Bags fetched:", bags);

      if (bags.length === 0) {
        bagsList.innerHTML = "<p>No surprise bags available at the moment.</p>";
        return;
      }

      bagsList.innerHTML = "";
      bags.forEach((bag) => {
        const bagCard = document.createElement("div");
        bagCard.className = "bag-card";
        bagCard.innerHTML = `
                    <img src="${
                      bag.image_urls?.[0] || "/images/placeholder.jpg"
                    }" alt="${bag.title}">
                    <h3>${bag.title}</h3>
                    <p>${bag.description || "No description available"}</p>
                    <p class="price">$${bag.discount_price.toFixed(
                      2
                    )} (Save $${(
          bag.original_price - bag.discount_price
        ).toFixed(2)})</p>
                    <p>Available: ${bag.quantity_available}</p>
                    <p>Pickup: ${new Date(
                      bag.pickup_start
                    ).toLocaleString()} - ${new Date(
          bag.pickup_end
        ).toLocaleString()}</p>
                    <a href="#" class="buy-btn" data-bag-id="${
                      bag.id
                    }">Buy Now</a>
                `;
        bagsList.appendChild(bagCard);
      });

      document.querySelectorAll(".buy-btn").forEach((button) => {
        button.addEventListener("click", (e) => {
          e.preventDefault();
          const bagId = button.getAttribute("data-bag-id");
          buyBag(bagId);
        });
      });
      return;
    } catch (error) {
      attempts++;
      console.error(`Attempt ${attempts} failed:`, error);
      if (attempts === maxRetries) {
        bagsList.innerHTML =
          "<p>Error loading surprise bags. Please try again later.</p>";
      }
      await new Promise((resolve) => setTimeout(resolve, 1000 * attempts));
    }
  }
}

async function buyBag(bagId) {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Please log in to purchase a surprise bag.");
    window.location.href = "/login.html";
    return;
  }

  try {
    const response = await fetch("/orders/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        bag_id: bagId,
        quantity: 1,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to place order");
    }

    const order = await response.json();
    alert(`Order placed successfully! Order ID: ${order.id}`);
    fetchBags();
  } catch (error) {
    console.error("Error placing order:", error);
    alert("Error placing order. Please try again.");
  }
}
