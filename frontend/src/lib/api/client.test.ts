import { describe, expect, it, vi } from 'vitest';

import { fetchBatchJob, submitReview } from './client';

describe('api client', () => {
	it('throws when review payload shape is invalid', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue({
				ok: true,
				json: async () => ({ bad: true })
			})
		);

		await expect(submitReview(new File(['text'], 'label.txt'), {})).rejects.toThrow(
			'invalid review response'
		);
	});

	it('returns a batch job when payload shape is valid', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue({
				ok: true,
				json: async () => ({
					job_id: '123',
					status: 'completed',
					item_count: 1,
					processed_count: 1,
					results: []
				})
			})
		);

		await expect(fetchBatchJob('123')).resolves.toMatchObject({ job_id: '123' });
	});
});
