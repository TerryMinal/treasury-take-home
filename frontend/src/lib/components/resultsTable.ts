import type { ChecklistItemResult, ReviewStatus } from '$lib/types/api';

export const reviewStatusLabels: Record<ReviewStatus, string> = {
	pass: 'Passed',
	review: 'Needs Human Review'
};

export function groupChecklistItems(
	items: ChecklistItemResult[]
): Array<[string, ChecklistItemResult[]]> {
	return Object.entries(
		items.reduce<Record<string, ChecklistItemResult[]>>((accumulator, item) => {
			accumulator[item.section] = [...(accumulator[item.section] ?? []), item];
			return accumulator;
		}, {})
	);
}
