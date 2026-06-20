import { describe, expect, it } from 'vitest';
import { reviewStatusLabels } from '../resultsTable';

describe('review status labels', () => {
	it('maps backend statuses to reviewer-friendly text', () => {
		expect(reviewStatusLabels.match).toBe('Match');
		expect(reviewStatusLabels.mismatch).toBe('Mismatch');
		expect(reviewStatusLabels.missing_label).toBe('Missing from label');
		expect(reviewStatusLabels.missing_application).toBe('Missing from application');
		expect(reviewStatusLabels.uncertain).toBe('Needs review');
	});
});
