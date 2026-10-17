// Almacenamiento de tokens en memoria + localStorage (persistencia de sesión).
const ACCESS = "cb_access";
const REFRESH = "cb_refresh";

export const tokenStore = {
  getAccess: () => localStorage.getItem(ACCESS),
  getRefresh: () => localStorage.getItem(REFRESH),
  set(access: string, refresh: string) {
    localStorage.setItem(ACCESS, access);
    localStorage.setItem(REFRESH, refresh);
  },
  setAccess(access: string) {
    localStorage.setItem(ACCESS, access);
  },
  clear() {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
  },
};
