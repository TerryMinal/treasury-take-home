import { describe, expect, it, vi } from 'vitest';

import { fetchBatchJob, submitBatch, submitReview } from './client';

describe('api client', () => {
	it('throws when review payload shape is invalid', async () => {
		vi.stubGlobal(
			'fetch',
			vi.fn().mockResolvedValue({
				ok: true,
				json: async () => ({ bad: true })
			})
		);

		await expect(submitReview(new File(['text'], 'label.txt'))).rejects.toThrow(
			'invalid review response'
		);
	});

	it('posts single review requests to the frontend proxy route', async () => {
		const fetchMock = vi.fn().mockResolvedValue({
			ok: true,
			json: async () => ({
				filename: 'label.txt',
				beverage_type: 'wine',
				beverage_type_label: 'Wine',
				overall_status: 'review',
				summary: 'Needs review',
				summary_counts: { total: 1, passed: 0, review: 1 },
				review_reasons: ['Needs human review'],
				checklist_items: [],
				extracted: {},
				ocr: {
					text: 'label',
					provider: 'text-passthrough',
					warnings: [],
					preprocessing_steps: []
				}
			})
		});
		vi.stubGlobal('fetch', fetchMock);

		await submitReview(new File(['text'], 'label.txt'));

		expect(fetchMock).toHaveBeenCalledWith(
			'/api/review',
			expect.objectContaining({ method: 'POST' })
		);
	});

	it('returns a batch job when payload shape is valid', async () => {
		const fetchMock = vi.fn().mockResolvedValue({
			ok: true,
			json: async () => ({
				job_id: '123',
				status: 'completed',
				item_count: 1,
				processed_count: 1,
				results: []
			})
		});
		vi.stubGlobal('fetch', fetchMock);

		await expect(fetchBatchJob('123')).resolves.toMatchObject({ job_id: '123' });
		expect(fetchMock).toHaveBeenCalledWith('/api/batch/123');
	});

	it('posts batch requests to the frontend proxy route', async () => {
		const fetchMock = vi.fn().mockResolvedValue({
			ok: true,
			json: async () => ({
				job_id: '123',
				status: 'completed',
				item_count: 1,
				processed_count: 1,
				results: []
			})
		});
		vi.stubGlobal('fetch', fetchMock);

		await submitBatch([new File(['text'], 'label-one.txt')]);

		expect(fetchMock).toHaveBeenCalledWith(
			'/api/batch',
			expect.objectContaining({ method: 'POST' })
		);
	});
});
