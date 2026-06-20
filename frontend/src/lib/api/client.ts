import type { ApplicationData, BatchJobResponse, ReviewResponse } from '$lib/types/api';

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || 'http://localhost:8000';

function assertReviewResponse(payload: unknown): ReviewResponse {
	if (!payload || typeof payload !== 'object' || !('fields' in payload) || !('ocr' in payload)) {
		throw new Error('Backend returned an invalid review response.');
	}
	return payload as ReviewResponse;
}

function assertBatchJobResponse(payload: unknown): BatchJobResponse {
	if (!payload || typeof payload !== 'object' || !('job_id' in payload) || !('results' in payload)) {
		throw new Error('Backend returned an invalid batch response.');
	}
	return payload as BatchJobResponse;
}

async function parseJson(response: Response): Promise<unknown> {
	const payload = await response.json().catch(() => null);
	if (!response.ok) {
		const message =
			payload && typeof payload === 'object' && 'detail' in payload && typeof payload.detail === 'string'
				? payload.detail
				: 'The server could not complete the request.';
		throw new Error(message);
	}
	return payload;
}

export async function submitReview(file: File, applicationData: ApplicationData): Promise<ReviewResponse> {
	const formData = new FormData();
	formData.set('label_file', file);
	formData.set('application_data', JSON.stringify(applicationData));

	const response = await fetch(`${API_BASE_URL}/review`, {
		method: 'POST',
		body: formData
	});

	const payload = await parseJson(response);
	return assertReviewResponse(payload);
}

export async function submitBatch(files: File[], applicationData: ApplicationData[]): Promise<BatchJobResponse> {
	const formData = new FormData();
	for (const file of files) {
		formData.append('label_files', file);
	}
	formData.set('application_data', JSON.stringify(applicationData));

	const response = await fetch(`${API_BASE_URL}/batch`, {
		method: 'POST',
		body: formData
	});

	const payload = await parseJson(response);
	return assertBatchJobResponse(payload);
}

export async function fetchBatchJob(jobId: string): Promise<BatchJobResponse> {
	const response = await fetch(`${API_BASE_URL}/batch/${jobId}`);
	const payload = await parseJson(response);
	return assertBatchJobResponse(payload);
}
