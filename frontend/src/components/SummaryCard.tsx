// src/components/SummaryCard.tsx
import React, { useState } from "react";

interface SummaryCardProps {
  data: {
    id: string;
    lines3: string;
    lines5: string;
    lines8: string;
  };
}

const SummaryCard: React.FC<SummaryCardProps> = ({ data }) => {
  const [level, setLevel] = useState<3 | 5 | 8>(3);

  const content =
    level === 3 ? data.lines3 : level === 5 ? data.lines5 : data.lines8;

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    alert("클립보드에 복사되었습니다!");
  };

  return (
    <div className="mt-8 w-full p-6 rounded-xl border border-gray-200 bg-white shadow-lg transition-all duration-300 ease-in-out">
      <pre className="whitespace-pre-wrap leading-relaxed text-gray-800 text-[15px]">
        {content}
      </pre>

      <div className="mt-6 flex items-center gap-2">
        <button
          onClick={() => setLevel(3)}
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            level === 3
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          3줄
        </button>
        <button
          onClick={() => setLevel(5)}
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            level === 5
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          5줄
        </button>
        <button
          onClick={() => setLevel(8)}
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            level === 8
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          8줄
        </button>
        <button
          onClick={handleCopy}
          className="ml-auto text-blue-600 hover:text-blue-800 transition-colors duration-200 text-sm font-medium"
        >
          복사하기
        </button>
      </div>
    </div>
  );
};

export default SummaryCard;