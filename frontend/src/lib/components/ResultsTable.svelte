<script lang="ts">
	import type { ReviewResponse } from '$lib/types/api';
	import { reviewStatusLabels } from './resultsTable';

	export let result: ReviewResponse;
</script>

<section class="panel">
	<header class="summary">
		<div>
			<h2>Review results for {result.filename}</h2>
			<p>{result.summary}</p>
		</div>
		<strong class={`badge ${result.overall_status}`}>{reviewStatusLabels[result.overall_status]}</strong>
	</header>

	<div class="table-wrap">
		<table>
			<thead>
				<tr>
					<th>Field</th>
					<th>Application</th>
					<th>Label</th>
					<th>Status</th>
					<th>Why</th>
				</tr>
			</thead>
			<tbody>
				{#each result.fields as field}
					<tr>
						<td>{field.display_name}</td>
						<td>{field.application_value ?? 'Not provided'}</td>
						<td>{field.extracted_value ?? 'Not detected'}</td>
						<td><span class={`badge ${field.status}`}>{reviewStatusLabels[field.status]}</span></td>
						<td>{field.explanation}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	{#if result.ocr.warnings.length}
		<div class="notice">
			<h3>OCR notes</h3>
			<ul>
				{#each result.ocr.warnings as warning}
					<li>{warning}</li>
				{/each}
			</ul>
		</div>
	{/if}
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

	.summary {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		align-items: start;
	}

	h2,
	h3,
	p {
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

	th {
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #6e6255;
	}

	.badge {
		display: inline-block;
		padding: 0.35rem 0.6rem;
		border-radius: 999px;
		font-size: 0.82rem;
		font-weight: 700;
	}

	.match {
		background: #dff4e6;
		color: #1f6b3a;
	}

	.mismatch {
		background: #fbe0de;
		color: #8a2f2a;
	}

	.missing_label,
	.missing_application,
	.uncertain {
		background: #f8ecd0;
		color: #7a5600;
	}

	.notice {
		padding: 1rem;
		border-radius: 0.8rem;
		background: #f9f4eb;
	}
</style>
