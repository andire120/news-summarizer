// src/components/UrlInputBar.tsx
import React, { type FormEvent } from "react";

interface UrlInputBarProps {
  url: string;
  setUrl: (url: string) => void;
  isPending: boolean;
  onSubmit: (e: FormEvent) => void;
}

const UrlInputBar: React.FC<UrlInputBarProps> = ({
  url,
  setUrl,
  isPending,
  onSubmit,
}) => {
  return (
    <form onSubmit={onSubmit} className="mt-8 w-full flex items-center gap-2">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="뉴스 링크를 붙여넣으세요"
        className="flex-1 rounded-xl border border-gray-300 px-4 py-2.5 shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
        required
      />
      <button
        type="submit"
        disabled={isPending || !url}
        className="rounded-xl bg-blue-600 text-white font-medium px-6 py-2.5 hover:bg-blue-700 disabled:bg-gray-400 transition-colors duration-200"
      >
        {isPending ? "요약 중..." : "요약하기"}
      </button>
    </form>
  );
};

export default UrlInputBar;