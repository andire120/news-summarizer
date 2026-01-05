// src/pages/Home.tsx
import React, { useState, type FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import UrlInputBar from "../components/UrlInputBar";
import SummaryCard from "../components/SummaryCard";

// SummaryResult 타입 정의를 백엔드 응답에 맞게 수정
type SummaryResult = {
  id: string;
  chars100: string;
  chars200: string;
  chars300: string;
};

const Home: React.FC = () => {
  const [url, setUrl] = useState<string>("");

  const {
    mutate,
    data,
    isPending,
    error,
  } = useMutation<
    SummaryResult, // 반환값 타입
    Error, // 에러 타입
    string // mutationFn의 파라미터(u) 타입
  >({
    mutationFn: async (u) => {
      const res = await fetch("http://127.0.0.1:8000/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: u }),
      });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }
      return res.json();
    },
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (url) {
      mutate(url);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 min-h-screen flex flex-col items-center">
      <h1 className="text-3xl font-bold text-center text-gray-800">
        뉴스 요약기
      </h1>
      <p className="text-lg mt-2 text-gray-600 text-center">
        뉴스 링크를 붙여넣으면 100자, 200자, 300자 내외로 요약해 드립니다.
      </p>

      <UrlInputBar
        url={url}
        setUrl={setUrl}
        isPending={isPending}
        onSubmit={handleSubmit}
      />

      {error && (
        <p className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg w-full text-center">
          요약 실패:{" "}
          {error.message.includes("422")
            ? "기사 본문을 가져올 수 없거나 너무 짧습니다."
            : "서버 오류가 발생했습니다."}
        </p>
      )}

      {isPending && (
        <div className="mt-8 w-full p-6 rounded-xl border border-gray-200 bg-white shadow-sm animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
        </div>
      )}

      {/* 데이터가 있을 때만 SummaryCard 컴포넌트를 렌더링 */}
      {data && <SummaryCard data={data} />}
    </div>
  );
};

export default Home;
