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
    showMessage(data.message, "green");

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
    showMessage(data.message, "green");

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

// deixar global pro HTML
window.login = login;
window.register = register;
window.logout = logout;
