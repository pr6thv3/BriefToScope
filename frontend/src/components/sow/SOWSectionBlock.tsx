"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Edit3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export function SOWSectionBlock({ title, content }: { title: string; content: string }) {
  const [displayedContent, setDisplayedContent] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(content);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Streaming text effect on mount
  useEffect(() => {
    let index = 0;
    const speed = Math.max(5, 50 - content.length * 0.1); // faster for longer text
    
    const interval = setInterval(() => {
      if (index < content.length) {
        setDisplayedContent(content.substring(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [content]);

  const handleRegenerate = () => {
    setIsRegenerating(true);
    setDisplayedContent("");
    
    // Mock regeneration
    setTimeout(() => {
      setIsRegenerating(false);
      const newContent = value + " (Regenerated for better clarity and alignment with modern agency standards.)";
      setValue(newContent);
      
      // Trigger stream again
      let idx = 0;
      const intv = setInterval(() => {
        if (idx < newContent.length) {
          setDisplayedContent(newContent.substring(0, idx + 1));
          idx++;
        } else {
          clearInterval(intv);
        }
      }, 15);
    }, 1500);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="group relative rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
    >
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold text-slate-800">{title}</h4>
        
        <div className="flex items-center gap-2 opacity-0 transition-opacity group-hover:opacity-100">
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-8 text-xs text-slate-500 hover:text-slate-900"
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit3 className="mr-1.5 size-3" />
            {isEditing ? "Done" : "Edit"}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            className="h-8 text-xs text-indigo-600 hover:bg-indigo-50 hover:text-indigo-700 border-indigo-200"
            onClick={handleRegenerate}
            disabled={isRegenerating}
          >
            <Sparkles className={`mr-1.5 size-3 ${isRegenerating ? "animate-spin" : ""}`} />
            Regenerate
          </Button>
        </div>
      </div>

      {isEditing ? (
        <Textarea
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setDisplayedContent(e.target.value);
          }}
          className="min-h-[100px] text-sm leading-relaxed text-slate-700"
        />
      ) : (
        <div className="relative text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
          {displayedContent}
          {displayedContent.length < (isRegenerating ? value.length : content.length) && (
            <span className="inline-block w-1.5 h-4 ml-1 align-middle bg-sky-500 animate-pulse" />
          )}
        </div>
      )}
    </motion.div>
  );
}
