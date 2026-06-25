import { env } from '$env/dynamic/private';

function getBackendBaseUrl(): string {
	return (env.BACKEND_PRIVATE_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');
}

export function getBackendUrl(path: string): string {
	const normalizedPath = path.startsWith('/') ? path : `/${path}`;
	return `${getBackendBaseUrl()}${normalizedPath}`;
}

export async function proxyMultipartPost(
	fetchFn: typeof fetch,
	request: Request,
	path: string
): Promise<Response> {
	const formData = await request.formData();
	const upstreamResponse = await fetchFn(getBackendUrl(path), {
		method: 'POST',
		body: formData
	});

	return buildProxyResponse(upstreamResponse);
}

export async function proxyGet(fetchFn: typeof fetch, path: string): Promise<Response> {
	const upstreamResponse = await fetchFn(getBackendUrl(path));
	return buildProxyResponse(upstreamResponse);
}

async function buildProxyResponse(upstreamResponse: Response): Promise<Response> {
	const body = await upstreamResponse.text();
	const contentType = upstreamResponse.headers.get('content-type') ?? 'application/json';

	return new Response(body, {
		status: upstreamResponse.status,
		headers: {
			'content-type': contentType
		}
	});
}
