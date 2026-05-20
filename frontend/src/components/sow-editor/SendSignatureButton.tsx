import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";

type SendSignatureButtonProps = {
  disabled?: boolean;
  onClick: () => void;
};

export function SendSignatureButton({
  disabled,
  onClick,
}: SendSignatureButtonProps) {
  return (
    <Button
      size="sm"
      className="h-9 gap-2 bg-slate-950 text-white hover:bg-slate-800"
      onClick={onClick}
      disabled={disabled}
    >
      <Send data-icon="inline-start" />
      Send for Signature
    </Button>
  );
}
