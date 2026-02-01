import React, { useState } from "react";
import axios from "axios";
import "./App.css";

// Умный выбор адреса: если в Vercel задана переменная, берем её. 
// Если нет (на ПК) — стучимся в локальный сервер.
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

interface StyleOption {
  id: string;
  name: string;
  description: string;
  gradient: string;
  icon: string;
}

interface AIRequest {
  prompt: string;
  context: string;
}

interface AIResponse {
  text: string;
  success: boolean;
}

const styleOptions: StyleOption[] = [
  {
    id: "minimal",
    name: "Минималистичный",
    description: "Чистый дизайн",
    gradient: "from-blue-500 to-cyan-500",
    icon: "📐",
  },
  {
    id: "corporate",
    name: "Корпоративный",
    description: "Профессиональный",
    gradient: "from-gray-700 to-gray-900",
    icon: "🏢",
  },
  {
    id: "creative",
    name: "Креативный",
    description: "Яркий стиль",
    gradient: "from-purple-600 to-pink-600",
    icon: "🎨",
  },
  {
    id: "luxury",
    name: "Люкс",
    description: "Элегантный",
    gradient: "from-yellow-400 to-amber-600",
    icon: "✨",
  },
];

function App() {
  const [logo, setLogo] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [selectedStyle, setSelectedStyle] = useState<string>("minimal");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  // AI Modal state
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiContext, setAiContext] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setLogo(e.target.files[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!logo) {
      setError("Пожалуйста, загрузите логотип");
      return;
    }

    const formData = new FormData();
    formData.append("logo", logo);
    formData.append("text", text);
    formData.append("style", selectedStyle);

    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      // ИСПОЛЬЗУЕМ ПЕРЕМЕННУЮ API_URL
      const response = await axios.post(
        `${API_URL}/generate`,
        formData,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `offer_${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Ошибка при генерации PDF. Проверьте, запущен ли бэкенд.");
    } finally {
      setLoading(false);
    }
  };

  const handleAIGenerate = async () => {
    if (!aiPrompt.trim()) {
      alert("Пожалуйста, введите что нужно написать");
      return;
    }

    setAiLoading(true);
    setAiResult("");

    try {
      // ИСПОЛЬЗУЕМ ПЕРЕМЕННУЮ API_URL
      const response = await axios.post<AIResponse>(
        `${API_URL}/ai/generate-text`,
        {
          prompt: aiPrompt,
          context: aiContext,
        }
      );

      if (response.data.success) {
        setAiResult(response.data.text);
        setText(response.data.text);
        setIsAIModalOpen(false);
        setAiPrompt("");
        setAiContext("");
      } else {
        alert("Не удалось сгенерировать текст. Попробуйте еще раз.");
      }
    } catch (err: any) {
      console.error(err);
      alert(err.response?.data?.detail || "Ошибка при генерации текста ИИ. Проверьте связь с сервером.");
    } finally {
      setAiLoading(false);
    }
  };

  const openAIModal = () => {
    setIsAIModalOpen(true);
    setAiResult("");
  };

  const closeAIModal = () => {
    setIsAIModalOpen(false);
    setAiPrompt("");
    setAiContext("");
    setAiResult("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 animate-gradient">
      <div className="max-w-5xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-blue-300 mb-4">
            PDF Generator Pro
          </h1>
          <p className="text-gray-200 text-xl max-w-2xl mx-auto">
            Создайте профессиональную презентацию за несколько секунд с помощью ИИ
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-10 shadow-2xl border border-white/20">
          {/* Logo Upload + Style Selection - One Line */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-8 mb-10 pb-8 border-b border-white/10">
            {/* Logo Upload - Left Side */}
            <div className="flex-1 min-w-[250px]">
              <label className="block text-white font-semibold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">🖼️</span>
                <span>Загрузите логотип</span>
              </label>
              <div className="border-2 border-dashed border-white/30 rounded-xl p-6 hover:border-blue-400 transition-all cursor-pointer bg-white/5">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                  id="logo-upload"
                />
                <label htmlFor="logo-upload" className="cursor-pointer">
                  {logo ? (
                    <div className="flex flex-col items-center">
                      <div className="w-32 h-32 rounded-lg overflow-hidden border-2 border-white/30 shadow-lg mb-4">
                        <img
                          src={URL.createObjectURL(logo)}
                          alt="Preview"
                          className="w-full h-full object-contain p-2 bg-white"
                        />
                      </div>
                      <p className="text-sm text-gray-300 text-center">
                        {logo.name.length > 20 ? logo.name.substring(0, 20) + '...' : logo.name}
                      </p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-3">
                        <span className="text-4xl">⬆️</span>
                      </div>
                      <p className="text-sm text-gray-400 text-center">
                        Нажмите для загрузки
                      </p>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Style Selection - Right Side */}
            <div className="flex-1 min-w-[250px]">
              <label className="block text-white font-semibold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">🎨</span>
                <span>Выберите стиль</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                {styleOptions.map((style) => (
                  <div
                    key={style.id}
                    onClick={() => setSelectedStyle(style.id)}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${
                      selectedStyle === style.id
                        ? `border-white bg-gradient-to-br ${style.gradient} text-white shadow-lg`
                        : "border-white/30 hover:border-white/50 bg-white/5 hover:bg-white/10"
                    }`}
                  >
                    <div className="text-3xl mb-2">{style.icon}</div>
                    <div className="text-center">
                      <h3 className="font-bold text-sm">{style.name}</h3>
                      <p className="text-xs opacity-90 mt-1">{style.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Text Input with AI */}
          <div className="space-y-4 mb-8">
            <label className="block text-white font-semibold text-lg flex items-center gap-2">
              <span className="text-2xl">✍️</span>
              <span>Текст презентации</span>
            </label>
            <div className="relative">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Введите текст для вашей презентации или нажмите кнопку ИИ..."
                rows={10}
                className="w-full p-6 border-2 border-white/20 rounded-2xl focus:ring-4 focus:ring-blue-500/30 focus:border-blue-400 transition-all resize-none bg-white/10 text-white placeholder-gray-400"
              />
              <button
                type="button"
                onClick={openAIModal}
                className="absolute top-4 right-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all shadow-xl hover:shadow-2xl flex items-center gap-2 font-semibold"
              >
                <span className="text-xl">🤖</span>
                <span>Сгенерировать ИИ</span>
              </button>
            </div>
            {text && (
              <div className="flex items-center gap-2 text-green-400 text-sm">
                <span className="text-lg">✅</span>
                <span>Текст готов для генерации PDF</span>
              </div>
            )}
          </div>

          {/* Submit Button - Full Width at Bottom */}
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={loading || !logo || !text}
            className={`w-full py-5 px-8 rounded-2xl font-bold text-xl transition-all transform ${
              loading || !logo || !text
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-600 to-purple-700 hover:from-blue-700 hover:to-purple-800 shadow-2xl hover:shadow-3xl hover:-translate-y-1"
            } text-white`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-3">
                <span className="animate-spin text-2xl">⏳</span>
                <span>Генерация PDF...</span>
              </span>
            ) : (
              "📄 Создать презентацию"
            )}
          </button>

          {/* Status Messages */}
          {error && (
            <div className="mt-6 p-5 bg-red-500/20 border border-red-500 rounded-xl text-red-300 flex items-center gap-3">
              <span className="text-2xl">❌</span>
              <span>{error}</span>
            </div>
          )}
          {success && (
            <div className="mt-6 p-5 bg-green-500/20 border border-green-500 rounded-xl text-green-300 flex items-center gap-3">
              <span className="text-2xl">✅</span>
              <span>Презентация успешно создана! Файл загружен.</span>
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
          <FeatureCard icon="⚡" title="Мгновенно" description="Создание за секунды" />
          <FeatureCard icon="🎨" title="Красиво" description="Профессиональные шаблоны" />
          <FeatureCard icon="🤖" title="ИИ-помощник" description="Генерация текста" />
          <FeatureCard icon="📱" title="Универсально" description="Работает на всех устройствах" />
        </div>

        {/* Footer with Credits */}
        <div className="mt-20 text-center py-8">
          <div className="inline-block bg-white/10 backdrop-blur-sm px-8 py-4 rounded-2xl border border-white/20">
            <p className="text-gray-200 text-lg mb-2">Сделано с ❤️ для вас</p>
            <a 
              href="https://github.com/alexeyBel0v" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl"
            >
              <span className="text-xl">👨‍💻</span>
              <span className="font-semibold">Мой профиль</span>
              <span className="text-xl">↗️</span>
            </a>
            <p className="text-gray-400 text-sm mt-3">
              © 2026 PDF Generator Pro. Все права защищены.
            </p>
          </div>
        </div>
      </div>

      {/* AI Modal */}
      {isAIModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gradient-to-br from-gray-900 to-black rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto border border-white/20">
            <div className="p-8 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 flex items-center gap-3">
                  <span className="text-4xl">🤖</span>
                  Генератор текста ИИ
                </h2>
                <button
                  onClick={closeAIModal}
                  className="text-gray-400 hover:text-white text-4xl transition-colors"
                >
                  ×
                </button>
              </div>
              <p className="text-gray-400 mt-3">
                Опишите, что нужно написать, и ИИ создаст профессиональный текст для вашей презентации.
              </p>
            </div>

            <div className="p-8 space-y-6">
              {/* Context Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-3">
                  Контекст / Тема (Опционально)
                </label>
                <input
                  type="text"
                  value={aiContext}
                  onChange={(e) => setAiContext(e.target.value)}
                  placeholder="Например: Бизнес-предложение, Продукт, Услуга..."
                  className="w-full p-4 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-white placeholder-gray-500"
                />
              </div>

              {/* Prompt Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-3">
                  Что нужно написать? *
                </label>
                <textarea
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Например: Создай продающий текст для презентации нового продукта. Опиши преимущества и призыв к действию..."
                  rows={6}
                  className="w-full p-4 bg-white/5 border border-white/20 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none text-white placeholder-gray-500"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Будьте конкретны в описании, чтобы получить лучший результат
                </p>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleAIGenerate}
                disabled={aiLoading || !aiPrompt.trim()}
                className={`w-full py-4 px-8 rounded-xl font-bold text-lg transition-all ${
                  aiLoading || !aiPrompt.trim()
                    ? "bg-gray-700 cursor-not-allowed"
                    : "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-xl"
                }`}
              >
                {aiLoading ? (
                  <span className="flex items-center justify-center gap-3">
                    <span className="animate-spin text-2xl">⏳</span>
                    <span>ИИ генерирует текст...</span>
                  </span>
                ) : (
                  "✨ Сгенерировать текст"
                )}
              </button>

              {/* AI Result */}
              {aiResult && (
                <div className="mt-6">
                  <label className="block text-sm font-semibold text-gray-300 mb-3">
                    Результат:
                  </label>
                  <div className="bg-white/5 border border-white/20 rounded-xl p-6 max-h-64 overflow-y-auto">
                    <p className="text-gray-200 whitespace-pre-wrap">{aiResult}</p>
                  </div>
                  <div className="mt-4 flex gap-3">
                    <button
                      onClick={() => {
                        setText(aiResult);
                        closeAIModal();
                      }}
                      className="flex-1 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors font-semibold"
                    >
                      ✅ Использовать этот текст
                    </button>
                    <button
                      onClick={() => setAiResult("")}
                      className="px-6 bg-gray-700 text-gray-300 rounded-xl hover:bg-gray-600 transition-colors"
                    >
                      🔄 Сгенерировать заново
                    </button>
                  </div>
                </div>
              )}

              {/* Examples */}
              <div className="mt-8 pt-8 border-t border-white/10">
                <h3 className="font-semibold text-gray-300 mb-4">Примеры промптов:</h3>
                <div className="space-y-3">
                  <ExamplePrompt
                    text="Создай продающий текст для презентации нового приложения для управления финансами. Опиши 3 ключевых преимущества и добавь призыв к скачиванию."
                    onClick={() => setAiPrompt("Создай продающий текст для презентации нового приложения для управления финансами. Опиши 3 ключевых преимущества и добавь призыв к скачиванию.")}
                  />
                  <ExamplePrompt
                    text="Напиши убедительное бизнес-предложение для потенциального инвестора. Опиши миссию компании, рыночную нишу и прогноз роста."
                    onClick={() => setAiPrompt("Напиши убедительное бизнес-предложение для потенциального инвестора. Опиши миссию компании, рыночную нишу и прогноз роста.")}
                  />
                  <ExamplePrompt
                    text="Создай текст для презентации нового продукта. Опиши проблему, решение и почему клиент должен выбрать именно нас."
                    onClick={() => setAiPrompt("Создай текст для презентации нового продукта. Опиши проблему, решение и почему клиент должен выбрать именно нас.")}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 text-center border border-white/10 hover:border-white/30 hover:bg-white/10 transition-all">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="font-bold text-white text-lg mb-2">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  );
}

function ExamplePrompt({ text, onClick }: { text: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 bg-blue-900/30 border border-blue-500/30 rounded-xl hover:bg-blue-900/50 hover:border-blue-500/50 transition-colors text-sm text-gray-300"
    >
      {text}
    </button>
  );
}

export default App;
