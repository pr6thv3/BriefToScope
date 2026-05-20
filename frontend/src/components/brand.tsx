import Link from "next/link";
import { FilePenLine } from "lucide-react";
import { cn } from "@/lib/utils";

type BrandProps = {
  href?: string;
  className?: string;
  markClassName?: string;
};

export function Brand({
  href = "/",
  className,
  markClassName,
}: BrandProps) {
  return (
    <Link
      href={href}
      className={cn("flex items-center gap-2 text-lg font-semibold", className)}
    >
      <span
        className={cn(
          "flex size-8 items-center justify-center rounded-lg bg-blue-600 text-white shadow-lg shadow-blue-600/25",
          markClassName
        )}
      >
        <FilePenLine className="size-4" aria-hidden="true" />
      </span>
      <span>BriefToScope</span>
    </Link>
  );
}
