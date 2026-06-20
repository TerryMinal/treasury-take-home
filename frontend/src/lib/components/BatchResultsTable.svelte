<script lang="ts">
	import type { BatchJobResponse } from '$lib/types/api';

	export let job: BatchJobResponse;
</script>

<section class="panel">
	<header>
		<h2>Batch job {job.job_id}</h2>
		<p>{job.processed_count} of {job.item_count} files processed.</p>
	</header>

	<div class="table-wrap">
		<table>
			<thead>
				<tr>
					<th>File</th>
					<th>Status</th>
					<th>Summary</th>
				</tr>
			</thead>
			<tbody>
				{#each job.results as item}
					<tr>
						<td>{item.filename}</td>
						<td>{item.status}</td>
						<td>{item.result?.summary ?? item.error ?? 'Waiting for processing.'}</td>
					</tr>
				{/each}
			</tbody>
		</table>
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

	.table-wrap {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th,
	td {
		padding: 0.85rem;
		border-top: 1px solid #eee4d7;
		text-align: left;
		vertical-align: top;
	}
</style>
