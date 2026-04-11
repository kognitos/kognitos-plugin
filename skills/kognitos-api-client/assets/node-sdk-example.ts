import Kognitos from '@kognitos/node';

const client = new Kognitos({
  token: process.env.KOGNITOS_TOKEN!,
  region: (process.env.KOGNITOS_REGION as 'us' | 'eu' | 'uk') || 'us',
  env: (process.env.KOGNITOS_ENV as 'prod' | 'dev') || 'prod',
});

export async function listAutomations(params: {
  organizationId: string;
  workspaceId: string;
}) {
  return client.automations.list({
    organizationId: params.organizationId,
    workspaceId: params.workspaceId,
    pageSize: 10,
  });
}
