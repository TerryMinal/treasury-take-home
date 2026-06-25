import type { RequestHandler } from './$types';

import { proxyMultipartPost } from '../proxy';

export const POST: RequestHandler = async ({ fetch, request }) => {
	return proxyMultipartPost(fetch, request, '/review');
};
