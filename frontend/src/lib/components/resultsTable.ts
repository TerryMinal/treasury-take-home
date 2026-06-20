import type { ReviewStatus } from '$lib/types/api';

export const reviewStatusLabels: Record<ReviewStatus, string> = {
	match: 'Match',
	mismatch: 'Mismatch',
	missing_label: 'Missing from label',
	missing_application: 'Missing from application',
	uncertain: 'Needs review'
};
