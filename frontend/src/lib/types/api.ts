export type ReviewStatus =
	| 'match'
	| 'mismatch'
	| 'missing_label'
	| 'missing_application'
	| 'uncertain';

export interface ApplicationData {
	brand_name?: string | null;
	class_type?: string | null;
	abv?: string | null;
	net_contents?: string | null;
	producer?: string | null;
	country_of_origin?: string | null;
	government_warning?: string | null;
}

export interface OcrResult {
	text: string;
	provider: string;
	warnings: string[];
}

export interface FieldReview {
	field: string;
	display_name: string;
	application_value?: string | null;
	extracted_value?: string | null;
	normalized_application_value?: string | null;
	normalized_extracted_value?: string | null;
	status: ReviewStatus;
	explanation: string;
}

export interface ReviewResponse {
	filename: string;
	overall_status: ReviewStatus;
	fields: FieldReview[];
	extracted: ApplicationData;
	ocr: OcrResult;
	summary: string;
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
