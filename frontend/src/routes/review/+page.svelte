<script lang="ts">
	import ApplicationForm from '$lib/components/ApplicationForm.svelte';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import ResultsTable from '$lib/components/ResultsTable.svelte';
	import { submitReview } from '$lib/api/client';
	import type { ApplicationData, ReviewResponse } from '$lib/types/api';

	let applicationData: ApplicationData = {};
	let files: FileList | null = null;
	let isSubmitting = false;
	let errorMessage = '';
	let result: ReviewResponse | null = null;

	async function handleSubmit() {
		errorMessage = '';
		result = null;

		const file = files?.item(0);
		if (!file) {
			errorMessage = 'Choose a label file before running the review.';
			return;
		}

		isSubmitting = true;
		try {
			result = await submitReview(file, applicationData);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'The review could not be completed.';
		} finally {
			isSubmitting = false;
		}
	}
</script>

<main class="shell stack">
	<section class="hero">
		<p>Single-label review</p>
		<h1>Compare one application against one label.</h1>
		<p>Upload a label, enter the application values, and review the extracted result side by side.</p>
	</section>

	<section class="card stack">
		<FileUpload bind:files label="Label artwork or OCR text fixture" />
		<ApplicationForm bind:value={applicationData} />
		<div class="actions">
			<button disabled={isSubmitting} on:click={handleSubmit}>
				{isSubmitting ? 'Reviewing label...' : 'Run review'}
			</button>
			<a class="button-link secondary" href="/">Back home</a>
		</div>
		{#if errorMessage}
			<p class="status error">{errorMessage}</p>
		{/if}
		{#if isSubmitting}
			<p class="status">Review in progress. This prototype keeps the response path simple and local-first.</p>
		{/if}
	</section>

	{#if result}
		<ResultsTable {result} />
	{/if}
</main>
