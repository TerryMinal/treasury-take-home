<script lang="ts">
	import { goto } from '$app/navigation';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import { submitBatch } from '$lib/api/client';

	let files: FileList | null = null;
	let isSubmitting = false;
	let errorMessage = '';

	async function handleSubmit() {
		errorMessage = '';
		if (!files || files.length === 0) {
			errorMessage = 'Choose at least one label file for batch review.';
			return;
		}

		isSubmitting = true;
		try {
			const job = await submitBatch(Array.from(files));
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
		<h1>Review several labels in one session.</h1>
		<p>
			Choose several label images and let the app review each one separately. You do not need to type
			JSON or fill out extra forms.
		</p>
	</section>

	<section class="card stack">
		<FileUpload bind:files label="Label images" multiple={true} />

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
