export interface ToolingItem {
  label: string;
}

export interface ToolingGroup {
  title: string;
  items: ToolingItem[];
}

export const toolingGroups: ToolingGroup[] = [
  {
    title: 'Core application stack',
    items: [
      { label: 'TypeScript' },
      { label: 'Node.js' },
      { label: 'React' },
      { label: 'Astro' },
      { label: 'Next.js' },
    ],
  },
  {
    title: 'Backend and data',
    items: [
      { label: 'PostgreSQL' },
      { label: 'Drizzle' },
      { label: 'Prisma' },
      { label: 'WebSockets' },
      { label: 'Event-driven flows' },
    ],
  },
  {
    title: 'Infrastructure and delivery',
    items: [
      { label: 'AWS' },
      { label: 'Azure' },
      { label: 'Docker' },
      { label: 'Terraform' },
      { label: 'GitHub Actions' },
      { label: 'CI/CD' },
    ],
  },
  {
    title: 'Automation and integrations',
    items: [
      { label: 'n8n' },
      { label: 'Make' },
      { label: 'Zapier' },
      { label: 'Webhooks' },
      { label: 'Linear' },
      { label: 'Slack' },
    ],
  },
  {
    title: 'Applied AI workflow',
    items: [
      { label: 'OpenAI / ChatGPT' },
      { label: 'Codex' },
      { label: 'Cursor' },
      { label: 'Structured outputs' },
      { label: 'Summaries, routing, review support' },
    ],
  },
];
