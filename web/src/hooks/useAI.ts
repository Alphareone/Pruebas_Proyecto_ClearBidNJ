import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/store/toast";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function useAI(propertyId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const showToast = useToast((s) => s.show);

  // Reiniciar el chat cuando cambias de propiedad
  useEffect(() => {
    setMessages([]);
  }, [propertyId]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || !propertyId) return;

    // 1. Agregamos el mensaje del usuario inmediatamente a la vista
    const userMessage: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      // 2. Enviamos el mensaje al backend (Ajusta la URL si tu endpoint se llama distinto)
      const response = await api.post<{ reply: string }>(
        `/ai/properties/${propertyId}/chat`,
        { message: text }
      );
      
      // 3. Agregamos la respuesta de la IA
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.data.reply },
      ]);
    } catch (error) {
      console.error("Error en chat de IA:", error);
      showToast("Error: No se pudo conectar con el asistente.");
    } finally {
      setLoading(false);
    }
  };

  return {
    messages,
    sendMessage,
    loading,
  };
}