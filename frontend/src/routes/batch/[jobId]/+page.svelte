<script lang="ts">
	import { onMount } from 'svelte';
	import BatchResultsTable from '$lib/components/BatchResultsTable.svelte';
	import { fetchBatchJob } from '$lib/api/client';
	import type { BatchJobResponse } from '$lib/types/api';

	export let data: { jobId: string };

	let job: BatchJobResponse | null = null;
	let errorMessage = '';
	let isLoading = true;

	async function loadJob() {
		try {
			job = await fetchBatchJob(data.jobId);
			errorMessage = '';
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'The batch job could not be loaded.';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		let timer: ReturnType<typeof setInterval> | undefined;
		void loadJob();
		timer = setInterval(() => {
			void loadJob();
		}, 4000);
		return () => {
			if (timer) {
				clearInterval(timer);
			}
		};
	});
</script>

<main class="shell stack">
	<section class="hero">
		<p>Batch status</p>
		<h1>Monitor queued review work.</h1>
		<p>Each label shows its detected beverage type and any reasons a person should take a closer look.</p>
	</section>

	<div class="actions">
		<a class="button-link secondary" href="/batch">Start another batch</a>
		<a class="button-link secondary" href="/">Back home</a>
	</div>

	{#if errorMessage}
		<p class="status error">{errorMessage}</p>
	{:else if isLoading}
		<p class="status">Loading batch job details...</p>
	{:else if job}
		<BatchResultsTable {job} />
	{/if}
</main>
