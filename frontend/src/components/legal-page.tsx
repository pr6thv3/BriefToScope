import { Brand } from "@/components/brand";

type LegalPageProps = {
  title: string;
  updated: string;
  intro: string;
  sections: Array<{ title: string; body: string }>;
};

export function LegalPage({ title, updated, intro, sections }: LegalPageProps) {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b bg-background/95">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-5">
          <Brand />
          <span className="text-sm text-muted-foreground">Updated {updated}</span>
        </div>
      </header>
      <article className="mx-auto max-w-4xl px-6 py-12">
        <div className="mb-10 space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight">{title}</h1>
          <p className="max-w-3xl text-lg leading-8 text-muted-foreground">{intro}</p>
        </div>
        <div className="space-y-8">
          {sections.map((section) => (
            <section key={section.title} className="space-y-3 border-t pt-6">
              <h2 className="text-xl font-semibold">{section.title}</h2>
              <p className="leading-7 text-muted-foreground">{section.body}</p>
            </section>
          ))}
        </div>
      </article>
    </main>
  );
}
