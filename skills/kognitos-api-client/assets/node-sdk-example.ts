import Kognitos from '@kognitos/node';

const client = new Kognitos({
  token: process.env.KOGNITOS_TOKEN!,
  region: (process.env.KOGNITOS_REGION as 'us' | 'eu' | 'uk') || 'us',
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
