import { Database, Code } from "lucide-react";
import React from "react";
import type { DataviewType } from "./DataviewNode";

export default function DataviewComponent({
    query,
    dataviewType,
}: {
    query: string;
    dataviewType: DataviewType;
}) {
    const isJS = dataviewType === "dataviewjs";

    return (
        <div className="my-4 border border-[#F0FF3D]/30 rounded-lg overflow-hidden bg-[#F0FF3D]/5">
            {/* Header */}
            <div className="px-4 py-2 bg-[#F0FF3D]/10 border-b border-[#F0FF3D]/30 flex items-center gap-2">
                {isJS ? (
                    <Code size={16} className="text-[#F0FF3D]" />
                ) : (
                    <Database size={16} className="text-[#F0FF3D]" />
                )}
                <span className="font-semibold text-xs text-[#F0FF3D]">
                    {isJS ? "DataviewJS" : "Dataview"}
                </span>
            </div>
            {/* Query */}
            <pre className="px-4 py-2 text-xs text-[#F0FF3D] whitespace-pre-wrap">
                {query}
            </pre>
        </div>
    );
}
