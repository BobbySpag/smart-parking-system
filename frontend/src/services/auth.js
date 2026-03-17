const TOKEN_KEY = 'smart_parking_token';

/**
 * Retrieve the stored JWT from localStorage.
 * @returns {string|null}
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Persist the JWT to localStorage.
 * @param {string} token
 */
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the stored JWT from localStorage.
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Return true when a token is present in localStorage.
 * @returns {boolean}
 */
export function isAuthenticated() {
  return Boolean(getToken());
}

/**
 * Decode the JWT payload and return the claims object.
 * Falls back to null on any error (expired, malformed, etc.).
 * @returns {object|null}
 */
export function getCurrentUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const payloadBase64 = token.split('.')[1];
    const decoded = JSON.parse(atob(payloadBase64.replace(/-/g, '+').replace(/_/g, '/')));
    // Check expiry
    if (decoded.exp && decoded.exp * 1000 < Date.now()) {
      removeToken();
      return null;
    }
    return decoded;
  } catch {
    return null;
  }
}

/**
 * Build an Authorization header object for use with fetch/axios.
 * @returns {{ Authorization: string }|{}}
 */
export function getAuthHeader() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}
