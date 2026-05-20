import { SOWEditorPage } from "@/components/sow-editor/SOWEditorPage";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function SOWPage({ params }: PageProps) {
  const { id } = await params;

  return (
    <SOWEditorPage sowId={id} />
  );
}
