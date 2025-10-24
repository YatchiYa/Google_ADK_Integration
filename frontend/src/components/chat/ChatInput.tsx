"use client";

import { useState, KeyboardEvent } from "react";
import {
  FaPaperPlane,
  FaImage,
  FaPaperclip,
  FaMicrophone,
  FaRobot,
} from "react-icons/fa";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  modelName?: string;
}

export default function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Mène ...",
  modelName = "Gemini 2.5 Pro",
}: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        {/* Input Area */}
        <div className="relative bg-white border border-gray-300 rounded-2xl shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 pr-32 resize-none border-none outline-none rounded-2xl text-gray-900 placeholder-gray-400 disabled:bg-gray-50 disabled:text-gray-400"
            style={{ minHeight: "52px", maxHeight: "200px" }}
          />

          {/* Action Buttons */}
          <div className="absolute right-2 bottom-2 flex items-center space-x-1">
            <button
              type="button"
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Attach file"
            >
              <FaPaperclip />
            </button>

            <button
              type="button"
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Add image"
            >
              <FaImage />
            </button>

            <button
              type="button"
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Voice input"
            >
              <FaMicrophone />
            </button>

            <button
              onClick={handleSend}
              disabled={!message.trim() || disabled}
              className="p-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
              title="Send message"
            >
              <FaPaperPlane />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
