import type { RequestHandler } from './$types';

import { proxyGet } from '../../proxy';

export const GET: RequestHandler = async ({ fetch, params }) => {
	return proxyGet(fetch, `/batch/${params.jobId}`);
};
