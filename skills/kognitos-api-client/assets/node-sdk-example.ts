import Kognitos from '@kognitos/node';

const client = new Kognitos({
  token: process.env.KOGNITOS_TOKEN!,
  region: 'us',
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
