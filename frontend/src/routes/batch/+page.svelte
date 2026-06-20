<script lang="ts">
	import { goto } from '$app/navigation';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import { submitBatch } from '$lib/api/client';
	import type { ApplicationData } from '$lib/types/api';

	let files: FileList | null = null;
	let applicationJson = '[\n  {}\n]';
	let isSubmitting = false;
	let errorMessage = '';

	async function handleSubmit() {
		errorMessage = '';
		if (!files || files.length === 0) {
			errorMessage = 'Choose at least one label file for batch review.';
			return;
		}

		let applicationData: ApplicationData[];
		try {
			const parsed = JSON.parse(applicationJson);
			if (!Array.isArray(parsed)) {
				throw new Error('Batch application data must be a JSON array.');
			}
			applicationData = parsed as ApplicationData[];
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Batch application data must be valid JSON.';
			return;
		}

		isSubmitting = true;
		try {
			const job = await submitBatch(Array.from(files), applicationData);
			await goto(`/batch/${job.job_id}`);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'The batch job could not be started.';
		} finally {
			isSubmitting = false;
		}
	}
</script>

<main class="shell stack">
	<section class="hero">
		<p>Batch review</p>
		<h1>Queue multiple labels for review in one session.</h1>
		<p>
			Upload several label files and provide matching application data as a JSON array. Each item is
			processed independently so one failure does not block the rest.
		</p>
	</section>

	<section class="card stack">
		<FileUpload bind:files label="Label files" multiple={true} />

		<label class="field">
			<span>Application data JSON array</span>
			<textarea
				bind:value={applicationJson}
				rows="12"
				placeholder={`[{"brand_name":"OLD TOM DISTILLERY"}]`}
			></textarea>
		</label>

		<div class="actions">
			<button disabled={isSubmitting} on:click={handleSubmit}>
				{isSubmitting ? 'Starting batch...' : 'Start batch review'}
			</button>
			<a class="button-link secondary" href="/">Back home</a>
		</div>

		{#if errorMessage}
			<p class="status error">{errorMessage}</p>
		{/if}
	</section>
</main>

<style>
	.field {
		display: grid;
		gap: 0.5rem;
		font-weight: 600;
	}

	textarea {
		border: 1px solid #b9b0a2;
		border-radius: 0.75rem;
		padding: 0.9rem;
		background: #fffdfa;
		font: inherit;
	}
</style>
