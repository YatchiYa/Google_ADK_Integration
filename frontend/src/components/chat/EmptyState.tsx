"use client";

import { FaRobot } from "react-icons/fa";

interface EmptyStateProps {
  agentName?: string;
  onExampleClick?: (example: string) => void;
}

export default function EmptyState({ agentName, onExampleClick }: EmptyStateProps) {
  const examples = [
    "What can you help me with?",
    "Explain quantum computing in simple terms",
    "Write a professional email",
    "Help me plan a project"
  ];

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full text-center">
        {/* Logo */}
        <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg">
          <FaRobot className="text-white text-3xl" />
        </div>

        {/* Title */}
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600 mb-3">
          Legal Index - Ai
        </h1>
        
        <p className="text-gray-500 mb-8">
          Votre Assistant IA Avancé pour la |
        </p>

        {/* Example Prompts */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => onExampleClick?.(example)}
              className="p-4 bg-white border border-gray-200 rounded-xl text-left hover:border-blue-300 hover:shadow-md transition-all group"
            >
              <p className="text-sm text-gray-700 group-hover:text-blue-600 transition-colors">
                {example}
              </p>
            </button>
          ))}
        </div>

        {/* Info Text */}
        <p className="text-xs text-gray-400">
          Start a conversation by typing a message below
        </p>
      </div>
    </div>
  );
}
