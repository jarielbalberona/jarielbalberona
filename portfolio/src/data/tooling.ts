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
      { label: 'Vite', icon: { name: 'vitejs', variant: 'plain' } },
      { label: 'Tailwind CSS v4', icon: { name: 'tailwindcss', variant: 'original' } },
      { label: 'shadcn/ui' },
      { label: 'Design tokens' },
      { label: 'TanStack Query' },
      { label: 'Zustand', icon: { name: 'zustand', variant: 'plain' } },
      { label: 'Redux migrations', icon: { name: 'redux', variant: 'original' } },
    ],
  },
  {
    title: 'Backend and data',
    items: [
      { label: 'Node.js', icon: { name: 'nodejs', variant: 'plain' } },
      { label: 'Express', icon: { name: 'express', variant: 'original' } },
      { label: 'REST APIs' },
      { label: 'PostgreSQL', icon: { name: 'postgresql', variant: 'plain' } },
      { label: 'Prisma', icon: { name: 'prisma', variant: 'original' } },
      { label: 'Drizzle ORM' },
      { label: 'Redis', icon: { name: 'redis', variant: 'plain' } },
      { label: 'WebSockets' },
    ],
  },
  {
    title: 'Platform and delivery',
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
    title: 'Architecture',
    items: [
      { label: 'Feature-based architecture' },
      { label: 'Modular systems' },
      { label: 'Layered / Clean architecture' },
      { label: 'Monorepos' },
      { label: 'Event-driven flows' },
      { label: 'Observability' },
      { label: 'Scalable frontend systems' },
    ],
  },
];
