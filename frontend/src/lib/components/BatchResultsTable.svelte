<script lang="ts">
	import type { BatchJobResponse } from '$lib/types/api';
	import { reviewStatusLabels } from './resultsTable';
	import ResultsTable from './ResultsTable.svelte';

	export let job: BatchJobResponse;
</script>

<section class="panel">
	<header>
		<h2>Batch job</h2>
		<p>{job.processed_count} of {job.item_count} files processed.</p>
	</header>

	<div class="stack">
		{#each job.results as item, index}
			<details class="item" open={index === 0}>
				<summary>
					<div class="summary-main">
						<strong>{item.filename}</strong>
						<span>{item.result?.beverage_type_label ?? 'Pending review'}</span>
					</div>
					<div class="summary-side">
						{#if item.result}
							<span class={`badge ${item.result.overall_status}`}>
								{reviewStatusLabels[item.result.overall_status]}
							</span>
						{:else}
							<span class="pending">{item.status}</span>
						{/if}
					</div>
				</summary>

				<div class="detail">
					{#if item.result}
						<ResultsTable result={item.result} />
					{:else if item.error}
						<p class="error">{item.error}</p>
					{:else}
						<p class="pending">This file is still waiting for processing.</p>
					{/if}
				</div>
			</details>
		{/each}
	</div>
</section>

<style>
	.panel {
		display: grid;
		gap: 1rem;
		padding: 1.25rem;
		border: 1px solid #d9cfbf;
		border-radius: 1rem;
		background: #fff;
	}

	header :global(*) {
		margin: 0;
	}

	.stack {
		display: grid;
		gap: 0.85rem;
	}

	.item {
		border: 1px solid #e7dccd;
		border-radius: 0.9rem;
		background: #fffdfa;
		overflow: hidden;
	}

	summary {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		padding: 1rem 1.1rem;
		cursor: pointer;
		list-style: none;
	}

	summary::-webkit-details-marker {
		display: none;
	}

	.summary-main {
		display: grid;
		gap: 0.2rem;
	}

	.summary-main span {
		color: #6e6255;
		font-size: 0.92rem;
	}

	.detail {
		padding: 0 1rem 1rem;
	}

	.badge {
		display: inline-block;
		padding: 0.35rem 0.6rem;
		border-radius: 999px;
		font-size: 0.82rem;
		font-weight: 700;
	}

	.pass {
		background: #dff4e6;
		color: #1f6b3a;
	}

	.review,
	.pending {
		background: #f8ecd0;
		color: #7a5600;
	}

	.error {
		margin: 0;
		color: #8a2f2a;
	}
</style>
