export interface ToolingItem {
  label: string;
}

export interface ToolingGroup {
  title: string;
  items: ToolingItem[];
}

export const toolingGroups: ToolingGroup[] = [
  {
    title: 'Systems',
    items: [
      { label: 'Backend architecture' },
      { label: 'APIs' },
      { label: 'Data flow' },
      { label: 'Event-driven design' },
    ],
  },
  {
    title: 'Infrastructure',
    items: [
      { label: 'AWS' },
      { label: 'Docker' },
      { label: 'Terraform' },
      { label: 'CI/CD' },
    ],
  },
  {
    title: 'Data',
    items: [
      { label: 'PostgreSQL' },
      { label: 'Redis' },
      { label: 'Reporting pipelines' },
    ],
  },
  {
    title: 'Automation',
    items: [
      { label: 'n8n' },
      { label: 'Make' },
      { label: 'Zapier' },
      { label: 'Webhooks' },
      { label: 'Workflow orchestration' },
    ],
  },
  {
    title: 'AI',
    items: [
      { label: 'OpenAI API' },
      { label: 'Structured outputs' },
      { label: 'Summarization' },
      { label: 'Classification' },
      { label: 'Decision support tooling' },
    ],
  },
];
