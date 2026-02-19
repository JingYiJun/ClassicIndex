"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Search,
  Loader2,
  BookOpen,
  AlertCircle,
  XCircle,
  SearchX,
  Info,
  SlidersHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import ResultCard from "@/components/result-card";
import { searchApi } from "@/lib/api";
import type { SearchResult } from "@/lib/api";

export default function SearchApp() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [topK, setTopK] = useState(10);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("classicindex-top-k");
      if (saved) setTopK(Number(saved));
    } catch {
      /* noop */
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("classicindex-top-k", String(topK));
    } catch {
      /* noop */
    }
  }, [topK]);

  const handleSearch = useCallback(async () => {
    setWarning(null);
    setError(null);

    if (!query.trim()) {
      setWarning("请输入搜索内容");
      return;
    }

    setIsLoading(true);
    setHasSearched(true);

    try {
      const data = await searchApi(query, topK);
      setResults(data.results || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "发生未知错误");
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [query, topK]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.nativeEvent.isComposing) {
      handleSearch();
    }
  };

  return (
    <div className="gradient-bg flex min-h-screen flex-col items-center px-4 py-10 md:px-8 md:py-16">
      {/* Title */}
      <h1 className="gradient-title mb-2 text-center text-4xl font-bold tracking-tight md:text-5xl">
        📚 经典著作索引
      </h1>
      <p className="mb-10 text-center text-lg text-muted-foreground md:mb-14">
        在浩瀚典籍中，寻觅思想的光芒
      </p>

      {/* Search Area */}
      <div className="w-full max-w-2xl">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你想要查找的内容，例如：资本主义的本质是什么..."
              className="h-12 rounded-xl border-2 border-secondary bg-background/50 pl-11 text-base transition-colors focus-visible:border-primary focus-visible:ring-primary/30"
            />
          </div>
          <Button
            onClick={handleSearch}
            disabled={isLoading}
            className="gradient-accent h-12 rounded-xl px-6 text-base font-semibold text-white transition-all hover:shadow-lg hover:shadow-primary/30"
          >
            {isLoading ? (
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            ) : (
              <Search className="mr-2 h-5 w-5" />
            )}
            搜索
          </Button>
        </div>

        {/* Top-K Control */}
        <div className="mt-3 flex items-center gap-3 text-sm text-muted-foreground">
          <SlidersHorizontal className="h-3.5 w-3.5 shrink-0" />
          <span className="shrink-0">结果数量</span>
          <Slider
            value={[topK]}
            onValueChange={(v) => setTopK(v[0])}
            min={1}
            max={20}
            step={1}
            className="max-w-36"
          />
          <span className="w-6 text-center font-medium text-primary">
            {topK}
          </span>
        </div>

        {/* Warning */}
        {warning && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-yellow-500/10 px-4 py-3 text-sm text-yellow-400">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {warning}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <XCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      <div className="mt-8 w-full max-w-3xl flex-1">
        {isLoading && (
          <div className="flex flex-col items-center gap-3 py-12 text-muted-foreground">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span>正在搜索经典著作...</span>
          </div>
        )}

        {!isLoading && hasSearched && results.length > 0 && (
          <>
            <div className="mb-4 flex items-center gap-2">
              <Info className="h-4 w-4 text-primary" />
              <span className="text-sm text-muted-foreground">
                找到{" "}
                <strong className="text-foreground">{results.length}</strong>{" "}
                个相关段落
              </span>
            </div>
            <div className="space-y-4">
              {results.map((result, idx) => (
                <ResultCard
                  key={`${result.book}-${result.page}-${idx}`}
                  result={result}
                  rank={idx + 1}
                />
              ))}
            </div>
          </>
        )}

        {!isLoading && hasSearched && results.length === 0 && !error && (
          <div className="flex flex-col items-center gap-3 py-16 text-muted-foreground">
            <SearchX className="h-16 w-16 opacity-40" />
            <h3 className="text-lg font-medium text-foreground/80">
              未找到相关内容
            </h3>
            <p className="text-sm">请尝试使用不同的关键词或表达方式</p>
          </div>
        )}

        {!hasSearched && !isLoading && (
          <div className="flex flex-col items-center gap-3 py-16 text-muted-foreground">
            <BookOpen className="h-16 w-16 opacity-30" />
            <p className="text-sm">输入关键词开始搜索</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-12 text-center text-sm text-muted-foreground/50">
        基于 Qwen Embedding + Milvus 构建的语义搜索引擎
      </div>
    </div>
  );
}
