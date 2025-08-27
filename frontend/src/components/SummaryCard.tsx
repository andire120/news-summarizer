// src/components/SummaryCard.tsx
import React, { useState } from "react";

interface SummaryCardProps {
  data: {
    id: string;
    chars100: string; // "lines3" -> "chars100"로 변경
    chars200: string; // "lines5" -> "chars200"로 변경
    chars300: string; // "lines8" -> "chars300"로 변경
  };
}

const SummaryCard: React.FC<SummaryCardProps> = ({ data }) => {
  // 상태 변수명을 명확하게 변경
  const [summaryLevel, setSummaryLevel] = useState<100 | 200 | 300>(100);

  // 선택된 요약 레벨에 따라 올바른 데이터를 가져오도록 수정
  const rawContent =
    summaryLevel === 100
      ? data.chars100
      : summaryLevel === 200
      ? data.chars200
      : data.chars300;

  // 요약문을 특정 글자 수 기준으로 줄바꿈하는 함수
  const formatContentWithBreaks = (text: string, charsPerLine: number) => {
    let formattedText = "";
    let lineLength = 0;

    // 텍스트를 단어 단위로 분리 (띄어쓰기 기준)
    const words = text.split(" ");
    
    words.forEach((word, index) => {
      // 다음 단어를 추가했을 때 글자 수를 초과하는지 확인
      if (lineLength + word.length + (index > 0 ? 1 : 0) > charsPerLine) {
        formattedText += "\n"; // 줄바꿈 추가
        lineLength = 0;
      }
      
      formattedText += (index > 0 ? " " : "") + word;
      lineLength += word.length + (index > 0 ? 1 : 0);
    });
    
    return formattedText;
  };

  // 선택된 레벨에 따라 줄바꿈된 컨텐츠를 생성
  const content = formatContentWithBreaks(rawContent, 30);

  const handleCopy = () => {
    const textarea = document.createElement("textarea");
    textarea.value = content;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand("copy");
      alert("클립보드에 복사되었습니다!");
    } catch (err) {
      console.error("복사 실패:", err);
    }
    document.body.removeChild(textarea);
  };

  return (
    <div className="mt-8 w-full p-6 rounded-xl border border-gray-200 bg-white shadow-lg transition-all duration-300 ease-in-out">
      <pre className="whitespace-pre-wrap leading-relaxed text-gray-800 text-[15px]">
        {content}
      </pre>

      <div className="mt-6 flex items-center gap-2">
        <button
          onClick={() => setSummaryLevel(100)} // 3 -> 100으로 변경
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            summaryLevel === 100
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          100자 요약
        </button>
        <button
          onClick={() => setSummaryLevel(200)} // 5 -> 200으로 변경
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            summaryLevel === 200
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          200자 요약
        </button>
        <button
          onClick={() => setSummaryLevel(300)} // 8 -> 300으로 변경
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            summaryLevel === 300
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-700 hover:bg-gray-300"
          }`}
        >
          300자 요약
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
