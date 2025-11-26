import { NodeKey } from "lexical";
import React from "react";

export default function WikiLinkComponent({
    noteName,
    nodeKey,
}: {
    noteName: string;
    nodeKey: NodeKey;
}) {
    const handleClick = () => {
        window.dispatchEvent(
            new CustomEvent("navigate-to-note", {
                detail: { noteName },
            })
        );
    };

    return (
        <span
            className="wiki-link cursor-pointer text-[#F0FF3D] hover:underline"
            onClick={handleClick}
            title={`Open ${noteName}`}
        >
            [[{noteName}]]
        </span>
    );
}
