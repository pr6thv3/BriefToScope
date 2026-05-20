"use client";

import { useState } from "react";
import { LoaderCircle, Mail, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

type SignatureModalProps = {
  open: boolean;
  isSending: boolean;
  onOpenChange: (open: boolean) => void;
  onSend: (recipientEmail: string) => Promise<void>;
};

export function SignatureModal({
  open,
  isSending,
  onOpenChange,
  onSend,
}: SignatureModalProps) {
  const [email, setEmail] = useState("client@lumaretail.co");

  async function handleSend() {
    await onSend(email);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md p-5">
        <DialogHeader>
          <DialogTitle>Send SOW for signature</DialogTitle>
          <DialogDescription>
            Confirm the recipient before creating the e-signature request.
          </DialogDescription>
        </DialogHeader>

        <label className="flex flex-col gap-2 text-sm font-medium">
          Recipient email
          <div className="flex items-center gap-2 rounded-lg border bg-white px-3">
            <Mail className="size-4 text-slate-400" aria-hidden="true" />
            <Input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="border-0 px-0 shadow-none focus-visible:ring-0"
              placeholder="client@example.com"
            />
          </div>
        </label>

        <div className="rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm leading-6 text-blue-950">
          Demo mode returns a mock signing link when DocuSign is not configured.
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSending}
          >
            Cancel
          </Button>
          <Button
            className="bg-slate-950 text-white hover:bg-slate-800"
            onClick={handleSend}
            disabled={isSending || !email.includes("@")}
          >
            {isSending ? (
              <LoaderCircle data-icon="inline-start" className="animate-spin" />
            ) : (
              <Send data-icon="inline-start" />
            )}
            Send request
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
