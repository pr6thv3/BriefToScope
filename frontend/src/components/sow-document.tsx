import { orderedSections } from "@/lib/sow";
import type { SOWContent } from "@/lib/types";

type SOWDocumentProps = {
  sow: SOWContent;
  clientName?: string;
};

export function SOWDocument({ sow, clientName }: SOWDocumentProps) {
  return (
    <article className="document-paper mx-auto w-full max-w-3xl bg-white px-6 py-8 text-slate-950 md:px-14 md:py-12">
      <header className="mb-10 border-b pb-6">
        <p className="text-sm font-medium uppercase tracking-normal text-blue-600">
          Statement of Work
        </p>
        <h1 className="mt-2 text-3xl font-semibold leading-tight">
          {clientName ? `${clientName} Project Scope` : "Project Scope"}
        </h1>
      </header>

      <div className="flex flex-col gap-8">
        {orderedSections.map((section) => {
          const value = sow[section.key];
          return (
            <section key={section.key} id={section.key}>
              <h2 className="mb-3 text-xl font-semibold">
                {section.title}
              </h2>
              {Array.isArray(value) ? (
                <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm leading-6 text-slate-800 md:text-base">
                  {value.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              ) : (
                <p className="text-sm leading-6 text-slate-800 md:text-base">
                  {value}
                </p>
              )}
            </section>
          );
        })}
      </div>
    </article>
  );
}
