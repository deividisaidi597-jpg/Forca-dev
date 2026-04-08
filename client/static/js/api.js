const BASE_URL = window.location.origin;

async function apiRequest(endpoint, method = "GET", body = null, auth = false) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (auth) {
    const token = localStorage.getItem("token");
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(BASE_URL + endpoint, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  const data = await response.json().catch(() => ({}));

  return { response, data };
}

// =========================
// 🔐 AUTH
// =========================
async function login(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (!username || !password) {
    showMessage("Please fill in all the fields!", "orange");
    return;
  }

  const { response, data } = await apiRequest("/login", "POST", {
    username,
    password,
  });

  if (response.ok) {
    localStorage.setItem("token", data.token);

    setTimeout(() => {
      window.location.href = "/dashboard";
    }, 1000);
  } else {
    showMessage(data.message, "red");
  }
}

async function register(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const { response, data } = await apiRequest("/register", "POST", {
    username,
    password,
  });

  if (response.ok) {
    setTimeout(() => {
      window.location.href = "/";
    }, 1500);
  } else {
    showMessage(data.message, "red");
  }
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

window.login = login;
window.register = register;
window.logout = logout;
window.apiRequest = apiRequest;
