"use client";

import type { SearchResult } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { FileText, BookOpen } from "lucide-react";

interface ResultCardProps {
  result: SearchResult;
  rank: number;
}

export default function ResultCard({ result, rank }: ResultCardProps) {
  const scorePercent = (result.score * 100).toFixed(1);

  return (
    <div className="group relative rounded-2xl border-l-4 border-l-primary bg-gradient-to-br from-secondary/90 to-background/95 p-5 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-primary/10">
      <div className="mb-3 flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-3">
          <span className="font-serif text-2xl font-bold text-primary">
            #{rank}
          </span>
          <Badge className="gradient-accent border-0 px-3 py-1 text-white">
            <FileText className="mr-1 h-3.5 w-3.5" />第 {result.page} 页
          </Badge>
        </div>
        <Badge
          variant="secondary"
          className="bg-secondary/60 font-mono text-success"
        >
          相似度: {scorePercent}%
        </Badge>
      </div>

      <p className="whitespace-pre-wrap text-[1.05rem] leading-relaxed text-foreground/90">
        {result.content}
      </p>

      <div className="mt-3 flex items-center gap-1.5 text-sm text-muted-foreground italic">
        <BookOpen className="h-3.5 w-3.5" />
        <span>——《{result.book}》</span>
      </div>
    </div>
  );
}
