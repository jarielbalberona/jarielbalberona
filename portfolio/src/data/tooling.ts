export interface ToolingItem {
  label: string;
  icon?: {
    name: string;
    variant: string;
  };
  note?: string;
}

export interface ToolingGroup {
  title: string;
  items: ToolingItem[];
}

export const toolingGroups: ToolingGroup[] = [
  {
    title: 'Frontend',
    items: [
      { label: 'React', icon: { name: 'react', variant: 'original' } },
      { label: 'TypeScript', icon: { name: 'typescript', variant: 'plain' } },
      { label: 'Next.js', icon: { name: 'nextjs', variant: 'original' } },
      { label: 'Astro', icon: { name: 'astro', variant: 'plain' } },
      { label: 'Tailwind CSS v4', icon: { name: 'tailwindcss', variant: 'original' } },
      { label: 'Design tokens' },
      { label: 'TanStack Query' },
    ],
  },
  {
    title: 'Backend',
    items: [
      { label: 'Go', icon: { name: 'go', variant: 'plain' } },
      { label: 'Node.js', icon: { name: 'nodejs', variant: 'plain' } },
      { label: 'Express', icon: { name: 'express', variant: 'original' } },
      { label: 'REST APIs' },
      { label: 'OpenAPI', icon: { name: 'openapi', variant: 'plain' } },
      { label: 'WebSockets' },
    ],
  },
  {
    title: 'Data',
    items: [
      { label: 'PostgreSQL', icon: { name: 'postgresql', variant: 'plain' } },
      { label: 'Prisma', icon: { name: 'prisma', variant: 'original' } },
      { label: 'Drizzle ORM' },
      { label: 'Redis', icon: { name: 'redis', variant: 'plain' } },
      { label: 'Data pipelines' },
      { label: 'Reporting systems' },
    ],
  },
  {
    title: 'Infrastructure',
    items: [
      { label: 'Docker', icon: { name: 'docker', variant: 'plain' } },
      { label: 'Terraform', icon: { name: 'terraform', variant: 'plain' } },
      { label: 'GitHub Actions', icon: { name: 'githubactions', variant: 'plain' } },
      { label: 'CI/CD' },
      { label: 'AWS', icon: { name: 'amazonwebservices', variant: 'plain-wordmark' }, note: 'ECS, S3, RDS, ECR, EC2, Route 53' },
      { label: 'Azure', icon: { name: 'azure', variant: 'plain' }, note: 'ADF, ADLS' },
      { label: 'Grafana', icon: { name: 'grafana', variant: 'plain' } },
      { label: 'Prometheus', icon: { name: 'prometheus', variant: 'original' } },
      { label: 'Loki' },
    ],
  },
  {
    title: 'Automation',
    items: [
      { label: 'n8n' },
      { label: 'Webhooks' },
      { label: 'Event-driven workflows' },
      { label: 'Background jobs' },
      { label: 'System orchestration' },
    ],
  },
  {
    title: 'AI',
    items: [
      { label: 'OpenAI API' },
      { label: 'Structured outputs' },
      { label: 'Summarization workflows' },
      { label: 'Classification workflows' },
      { label: 'Decision support tooling' },
    ],
  },
  {
    title: 'Testing and verification',
    items: [
      { label: 'Vitest', icon: { name: 'vitest', variant: 'plain' } },
      { label: 'Playwright', icon: { name: 'playwright', variant: 'plain' } },
      { label: 'Go test', icon: { name: 'go', variant: 'plain' } },
      { label: 'API integration tests' },
      { label: 'Snapshot tests' },
      { label: 'Regression checks' },
    ],
  },
  {
    title: 'Architecture',
    items: [
      { label: 'Modular systems' },
      { label: 'Layered / Clean architecture' },
      { label: 'Event-driven flows' },
      { label: 'Observability' },
      { label: 'Operational reliability' },
      { label: 'System boundaries' },
    ],
  },
];
