import { describe, expect, it, vi } from 'vitest';

import { getBackendUrl, proxyGet, proxyMultipartPost } from './proxy';

describe('backend proxy helpers', () => {
	it('uses localhost backend by default', () => {
		expect(getBackendUrl('/health')).toBe('http://localhost:8000/health');
	});

	it('proxies multipart posts and preserves upstream errors', async () => {
		const fetchMock = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ detail: 'Uploaded label file was empty.' }), {
				status: 400,
				headers: { 'content-type': 'application/json' }
			})
		);
		const request = new Request('http://frontend.test/api/review', {
			method: 'POST',
			body: new FormData()
		});

		const response = await proxyMultipartPost(fetchMock, request, '/review');

		expect(fetchMock).toHaveBeenCalledWith(
			'http://localhost:8000/review',
			expect.objectContaining({ method: 'POST' })
		);
		expect(response.status).toBe(400);
		await expect(response.json()).resolves.toEqual({ detail: 'Uploaded label file was empty.' });
	});

	it('proxies get requests to the backend', async () => {
		const fetchMock = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ job_id: 'job-123', results: [] }), {
				status: 200,
				headers: { 'content-type': 'application/json' }
			})
		);

		const response = await proxyGet(fetchMock, '/batch/job-123');

		expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/batch/job-123');
		expect(response.status).toBe(200);
		await expect(response.json()).resolves.toEqual({ job_id: 'job-123', results: [] });
	});
});
