// Store simple de toasts.
import { create } from "zustand";

interface ToastState {
  message: string | null;
  show: (msg: string) => void;
  hide: () => void;
}

let timer: ReturnType<typeof setTimeout> | undefined;

export const useToast = create<ToastState>((set) => ({
  message: null,
  show: (msg) => {
    set({ message: msg });
    clearTimeout(timer);
    timer = setTimeout(() => set({ message: null }), 1900);
  },
  hide: () => set({ message: null }),
}));
