document.addEventListener("DOMContentLoaded", () => {
  const ordersList = document.getElementById("ordersList");

  async function fetchOrders() {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("Please log in to view your orders.");
      }

      const response = await fetch("http://127.0.0.1:8000/orders", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch orders");
      const orders = await response.json();
      renderOrders(orders);
    } catch (error) {
      ordersList.innerHTML = `<p class="error">${error.message}</p>`;
      console.error(error);
    }
  }

  function renderOrders(orders) {
    ordersList.innerHTML = "";
    if (orders.length === 0) {
      ordersList.innerHTML = "<p>No orders found.</p>";
      return;
    }

    orders.forEach((order) => {
      const orderCard = document.createElement("div");
      orderCard.className = "order-card";
      orderCard.innerHTML = `
                <h3>Order #${order.id}</h3>
                <p>Bag: ${order.bag_id}</p>
                <p>Total: $${order.total_price}</p>
                <p class="status">Status: ${order.status}</p>
            `;
      ordersList.appendChild(orderCard);
    });
  }

  fetchOrders();
});
