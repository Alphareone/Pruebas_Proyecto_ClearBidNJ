import { useState } from 'react';
import { api } from '@/lib/api';

export default function FloatingAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'ai', text: '¡Hola! Soy tu asistente de ClearBid NJ. ¿En qué te puedo ayudar hoy?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userText = input;
    setMessages((prev) => [...prev, { role: 'user', text: userText }]);
    setInput('');
    setLoading(true);

    try {
      // Usamos la instancia oficial de api para evitar errores de conexión/CORS
      const response = await api.post('/ai/chat', { message: userText });
      setMessages((prev) => [...prev, { role: 'ai', text: response.data.reply }]);
    } catch (error) {
      console.error("Error AI:", error);
      setMessages((prev) => [...prev, { role: 'ai', text: 'Error: No me pude conectar con el servidor. Revisa tu conexión.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end">
      {isOpen && (
        <div className="bg-paper border border-line2 rounded-xl shadow-2xl w-[350px] h-[450px] flex flex-col mb-4 overflow-hidden">
          <div className="p-3 bg-[var(--accent)] text-[var(--ink)] font-bold flex justify-between items-center">
            <span>Asistente IA</span>
            <button onClick={() => setIsOpen(false)} className="text-xl hover:opacity-70">✕</button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-wash">
            {messages.map((m, i) => (
              <div 
                key={i} 
                className={`p-2.5 rounded-lg text-[13px] max-w-[85%] ${
                  m.role === 'ai' 
                    ? 'bg-blue-100 text-blue-900 self-start rounded-tl-none' 
                    : 'bg-[var(--accent)] text-[var(--ink)] self-end ml-auto rounded-tr-none'
                }`}
              >
                {m.text}
              </div>
            ))}
            {loading && <div className="text-ink2 text-xs italic">Escribiendo...</div>}
          </div>
          
          <div className="p-3 bg-paper border-t border-line2 flex gap-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              className="flex-1 rounded-md border border-line2 px-3 py-2 text-[13px] focus:outline-none focus:border-accent" 
              placeholder="Escribe tu duda..." 
            />
            <button 
              onClick={sendMessage} 
              disabled={loading || !input.trim()}
              className="btn px-4 disabled:opacity-50"
              style={{ background: "var(--accent)", color: "var(--ink)" }}
            >
              Enviar
            </button>
          </div>
        </div>
      )}
      
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="rounded-full shadow-lg h-14 w-14 flex items-center justify-center text-2xl transition-transform hover:scale-105"
        style={{ background: "var(--accent)" }}
      >
        💬
      </button>
    </div>
  );
}