"use client";

import { useState } from "react";
import { Loader2, Mail, Send, ShieldCheck, FileSignature } from "lucide-react";
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
import { Textarea } from "@/components/ui/textarea";

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
  const [clientName, setClientName] = useState("Luma Retail Decision Maker");
  const [subject, setSubject] = useState("Agreement: Brand Identity + Webflow Website SOW");
  const [message, setMessage] = useState(
    "Hi there, please review and e-sign this Statement of Work for our upcoming project. Let me know if you have any questions!"
  );

  async function handleSend() {
    await onSend(email);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg p-6 bg-white border border-slate-200 shadow-2xl rounded-2xl">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <div className="flex size-10 items-center justify-center rounded-xl bg-slate-900 text-white">
              <FileSignature className="size-5" />
            </div>
            <div>
              <DialogTitle className="text-lg font-bold text-slate-900">
                E-Sign Envelope Handoff
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-400">
                Configure client signing invitation and email template parameters.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 my-4">
          <div className="grid grid-cols-2 gap-4">
            <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-700">
              Recipient Name
              <Input
                type="text"
                value={clientName}
                onChange={(event) => setClientName(event.target.value)}
                className="h-9 text-xs border-slate-200 focus-visible:ring-1 focus-visible:ring-indigo-500"
                placeholder="Client Name"
              />
            </label>
            <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-700">
              Recipient Email
              <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 h-9 focus-within:ring-1 focus-within:ring-indigo-500 focus-within:border-indigo-500">
                <Mail className="size-3.5 text-slate-400" aria-hidden="true" />
                <Input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="border-0 p-0 text-xs shadow-none focus-visible:ring-0 h-full"
                  placeholder="client@example.com"
                />
              </div>
            </label>
          </div>

          <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-700">
            Email Subject Line
            <Input
              type="text"
              value={subject}
              onChange={(event) => setSubject(event.target.value)}
              className="h-9 text-xs border-slate-200 focus-visible:ring-1 focus-visible:ring-indigo-500"
            />
          </label>

          <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-700">
            Custom Message to Signer
            <Textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              className="min-h-[80px] text-xs leading-relaxed border-slate-200 focus-visible:ring-1 focus-visible:ring-indigo-500"
            />
          </label>

          <div className="rounded-xl border border-indigo-100 bg-indigo-50/60 p-3.5 flex gap-2.5 items-start">
            <ShieldCheck className="size-4.5 text-indigo-600 shrink-0 mt-0.5" />
            <div className="text-[11px] leading-relaxed text-indigo-950">
              <span className="font-bold">DocuSign sandbox integration:</span> This will assemble the JSON schema and render a mock signature package if credentials are unconfigured.
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0 border-t pt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onOpenChange(false)}
            disabled={isSending}
            className="h-9"
          >
            Cancel
          </Button>
          <Button
            size="sm"
            className="h-9 bg-slate-950 text-white hover:bg-slate-900 gap-1.5 shadow-sm"
            onClick={handleSend}
            disabled={isSending || !email.includes("@") || !clientName}
          >
            {isSending ? (
              <Loader2 className="size-3.5 animate-spin" />
            ) : (
              <Send className="size-3.5" />
            )}
            <span>{isSending ? "Creating envelope..." : "Send via DocuSign"}</span>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
