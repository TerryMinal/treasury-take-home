	<script lang="ts">
		import type { ChecklistItemResult, ReviewResponse } from '$lib/types/api';
		import { groupChecklistItems, reviewStatusLabels } from './resultsTable';

	export let result: ReviewResponse;

	let groupedItems: [string, ChecklistItemResult[]][] = [];

	$: groupedItems = groupChecklistItems(result.checklist_items);
</script>

<section class="panel">
	<header class="summary">
		<div>
			<p class="eyebrow">{result.beverage_type_label}</p>
			<h2>Compliance review for {result.filename}</h2>
			<p>{result.summary}</p>
		</div>
		<strong class={`badge ${result.overall_status}`}>{reviewStatusLabels[result.overall_status]}</strong>
	</header>

	<div class="metrics">
		<div>
			<span class="metric-label">Checks passed</span>
			<strong>{result.summary_counts.passed}</strong>
		</div>
		<div>
			<span class="metric-label">Needs review</span>
			<strong>{result.summary_counts.review}</strong>
		</div>
		<div>
			<span class="metric-label">Detected type</span>
			<strong>{result.beverage_type_label}</strong>
		</div>
	</div>

	{#if result.review_reasons.length}
		<div class="notice review">
			<h3>Why this needs human review</h3>
			<ul>
				{#each result.review_reasons as reason}
					<li>{reason}</li>
				{/each}
			</ul>
		</div>
	{/if}

	{#each groupedItems as [section, items]}
		<section class="checklist-group">
			<header class="group-header">
				<h3>{section}</h3>
				<p>{items.filter((item) => item.status === 'review').length} review item(s)</p>
			</header>

			<div class="table-wrap">
				<table>
					<thead>
						<tr>
							<th>Checklist item</th>
							<th>Requirement</th>
							<th>Status</th>
							<th>Evidence</th>
							<th>Explanation</th>
						</tr>
					</thead>
					<tbody>
						{#each items as item}
							<tr>
								<td>{item.label}</td>
								<td>{item.requirement_level}</td>
								<td><span class={`badge ${item.status}`}>{reviewStatusLabels[item.status]}</span></td>
								<td>{item.evidence_text ?? 'No clear evidence detected'}</td>
								<td>
									<p>{item.explanation}</p>
									{#if item.review_reasons.length}
										<ul class="reason-list">
											{#each item.review_reasons as reason}
												<li>{reason}</li>
											{/each}
										</ul>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>
	{/each}

	<!-- {#if result.ocr.warnings.length || result.ocr.preprocessing_steps.length}
		<div class="notice">
			<h3>OCR notes</h3>
			{#if result.ocr.preprocessing_steps.length}
				<p>Preprocessing: {result.ocr.preprocessing_steps.join(', ')}</p>
			{/if}
			{#if result.ocr.warnings.length}
				<ul>
					{#each result.ocr.warnings as warning}
						<li>{warning}</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if} -->
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

	.eyebrow {
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-size: 0.78rem;
		color: #8a4b2a;
	}

	.metrics {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		gap: 0.75rem;
	}

	.metrics div {
		padding: 0.9rem 1rem;
		border-radius: 0.8rem;
		background: #f9f4eb;
	}

	.metric-label {
		display: block;
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #6e6255;
	}

	.checklist-group {
		display: grid;
		gap: 0.75rem;
	}

	.group-header {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		align-items: baseline;
	}

	.group-header :global(*) {
		margin: 0;
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

	.pass {
		background: #dff4e6;
		color: #1f6b3a;
	}

	.review {
		background: #f8ecd0;
		color: #7a5600;
	}

	.notice {
		padding: 1rem;
		border-radius: 0.8rem;
		background: #f9f4eb;
	}

	.reason-list,
	.notice ul {
		margin: 0.5rem 0 0;
		padding-left: 1.1rem;
	}
</style>
