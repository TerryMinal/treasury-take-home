<script lang="ts">
	import FileUpload from '$lib/components/FileUpload.svelte';
	import ResultsTable from '$lib/components/ResultsTable.svelte';
	import { submitReview } from '$lib/api/client';
	import type { ReviewResponse } from '$lib/types/api';

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
			result = await submitReview(file);
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
		<h1>Upload one label and run the TTB compliance checklist.</h1>
		<p>
			The app reads the label, detects the beverage type, and shows green checks for passed items and
			yellow follow-ups for anything a reviewer should confirm.
		</p>
	</section>

	<section class="card stack">
		<FileUpload bind:files label="Label image" />
		<div class="actions">
			<button disabled={isSubmitting} on:click={handleSubmit}>
				{isSubmitting ? 'Reviewing label...' : 'Run compliance review'}
			</button>
			<a class="button-link secondary" href="/">Back home</a>
		</div>
		{#if errorMessage}
			<p class="status error">{errorMessage}</p>
		{/if}
		{#if isSubmitting}
			<p class="status">Review in progress. The app is reading the label and checking it against the TTB checklist.</p>
		{/if}
	</section>

	{#if result}
		<ResultsTable {result} />
	{/if}
</main>
