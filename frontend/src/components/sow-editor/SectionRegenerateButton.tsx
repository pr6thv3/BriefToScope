import { LoaderCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

type SectionRegenerateButtonProps = {
  isRegenerating: boolean;
  onRegenerate: () => void;
};

export function SectionRegenerateButton({
  isRegenerating,
  onRegenerate,
}: SectionRegenerateButtonProps) {
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className="h-8 gap-1.5 border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100"
      onClick={onRegenerate}
      disabled={isRegenerating}
    >
      {isRegenerating ? (
        <LoaderCircle data-icon="inline-start" className="animate-spin" />
      ) : (
        <Sparkles data-icon="inline-start" />
      )}
      {isRegenerating ? "Rewriting" : "Regenerate"}
    </Button>
  );
}
