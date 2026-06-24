import { describe, expect, it } from 'vitest';
import { groupChecklistItems, reviewStatusLabels } from '../resultsTable';

describe('review status labels', () => {
	it('maps backend statuses to reviewer-friendly text', () => {
		expect(reviewStatusLabels.pass).toBe('Passed');
		expect(reviewStatusLabels.review).toBe('Needs Human Review');
	});

	it('groups checklist items by section', () => {
		const groups = groupChecklistItems([
			{
				id: 'brand_name',
				label: 'Brand Name',
				section: 'Brand Label',
				requirement_level: 'required',
				evaluation_type: 'text_presence',
				status: 'pass',
				explanation: 'Found brand name.',
				review_reasons: [],
				evidence_text: 'Harbor Gold'
			},
			{
				id: 'government_warning',
				label: 'Government Warning Statement',
				section: 'Any Label',
				requirement_level: 'required',
				evaluation_type: 'exact_warning',
				status: 'review',
				explanation: 'Review this item.',
				review_reasons: ['Needs review'],
				evidence_text: null
			}
		]);

		expect(groups).toEqual([
			[
				'Brand Label',
				[
					expect.objectContaining({
						id: 'brand_name'
					})
				]
			],
			[
				'Any Label',
				[
					expect.objectContaining({
						id: 'government_warning'
					})
				]
			]
		]);
	});
});
