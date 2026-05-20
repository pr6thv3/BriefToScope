import { FileDown, LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

type ExportPDFButtonProps = {
  isExporting: boolean;
  onExport: () => void;
};

export function ExportPDFButton({ isExporting, onExport }: ExportPDFButtonProps) {
  return (
    <Button
      variant="outline"
      size="sm"
      className="h-9 gap-2 bg-white"
      onClick={onExport}
      disabled={isExporting}
    >
      {isExporting ? (
        <LoaderCircle data-icon="inline-start" className="animate-spin" />
      ) : (
        <FileDown data-icon="inline-start" />
      )}
      {isExporting ? "Exporting" : "Export PDF"}
    </Button>
  );
}
