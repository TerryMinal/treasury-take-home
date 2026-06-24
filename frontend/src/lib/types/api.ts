export type ReviewStatus = 'pass' | 'review';

export type BeverageType = 'wine' | 'distilled_spirits' | 'malt_beverage';

export type RequirementLevel = 'required' | 'conditional';

export interface ExtractedLabelData {
	brand_name?: string | null;
	designation?: string | null;
	alcohol_content?: string | null;
	net_contents?: string | null;
	name_and_address?: string | null;
	government_warning?: string | null;
	country_of_origin?: string | null;
	appellation_of_origin?: string | null;
	sulfite_declaration?: string | null;
	yellow_5_declaration?: string | null;
	cochineal_or_carmine_declaration?: string | null;
	aspartame_declaration?: string | null;
	coloring_statement?: string | null;
	treatment_with_wood_statement?: string | null;
	commodity_statement?: string | null;
	state_of_distillation?: string | null;
	age_statement?: string | null;
	is_imported?: boolean | null;
	raw_text_excerpt?: string | null;
}

export interface OcrResult {
	text: string;
	provider: string;
	warnings: string[];
	preprocessing_steps: string[];
}

export interface ChecklistItemResult {
	id: string;
	label: string;
	section: string;
	requirement_level: RequirementLevel;
	evaluation_type: string;
	status: ReviewStatus;
	explanation: string;
	review_reasons: string[];
	evidence_text?: string | null;
}

export interface ReviewSummaryCounts {
	total: number;
	passed: number;
	review: number;
}

export interface ReviewResponse {
	filename: string;
	beverage_type?: BeverageType | null;
	beverage_type_label: string;
	overall_status: ReviewStatus;
	summary: string;
	summary_counts: ReviewSummaryCounts;
	review_reasons: string[];
	checklist_items: ChecklistItemResult[];
	extracted: ExtractedLabelData;
	ocr: OcrResult;
}

export interface BatchReviewItem {
	filename: string;
	status: string;
	result?: ReviewResponse | null;
	error?: string | null;
}

export interface BatchJobResponse {
	job_id: string;
	status: string;
	item_count: number;
	processed_count: number;
	results: BatchReviewItem[];
}
