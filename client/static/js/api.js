const API_URL = "";

async function apiRequest(path, method = "GET", body = null, auth = false) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (auth) {
    const token = localStorage.getItem("token");
    headers["Authorization"] = "Bearer " + token;
  }

  const response = await fetch(API_URL + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  let data;

  try {
    data = await response.json();
  } catch (e) {
    data = { message: "Server error (no JSON returned)" };
  }
  return { response, data };
}
