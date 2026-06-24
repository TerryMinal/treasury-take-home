<script lang="ts">
	interface LegacyApplicationData {
		brand_name?: string | null;
		class_type?: string | null;
		abv?: string | null;
		net_contents?: string | null;
		producer?: string | null;
		country_of_origin?: string | null;
		government_warning?: string | null;
	}

	export let value: LegacyApplicationData;

	const fields: Array<{ key: keyof LegacyApplicationData; label: string; placeholder: string }> = [
		{ key: 'brand_name', label: 'Brand name', placeholder: 'OLD TOM DISTILLERY' },
		{ key: 'class_type', label: 'Class / type', placeholder: 'Kentucky Straight Bourbon Whiskey' },
		{ key: 'abv', label: 'Alcohol content / ABV', placeholder: '45% Alc./Vol. (90 Proof)' },
		{ key: 'net_contents', label: 'Net contents', placeholder: '750 mL' },
		{ key: 'producer', label: 'Name and address', placeholder: 'Bottled by Old Tom Distillery, Frankfort, KY' },
		{ key: 'country_of_origin', label: 'Country of origin', placeholder: 'Product of Mexico' }
	];
</script>

<div class="grid">
	{#each fields as field}
		<label class="field">
			<span>{field.label}</span>
			<input bind:value={value[field.key]} placeholder={field.placeholder} />
		</label>
	{/each}

	<label class="field warning">
		<span>Government warning</span>
		<textarea
			bind:value={value.government_warning}
			rows="5"
			placeholder="Paste the exact government warning text from the application."
		></textarea>
	</label>
</div>

<style>
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 1rem;
	}

	.field {
		display: grid;
		gap: 0.45rem;
		font-weight: 600;
	}

	.warning {
		grid-column: 1 / -1;
	}

	input,
	textarea {
		border: 1px solid #b9b0a2;
		border-radius: 0.75rem;
		padding: 0.85rem 1rem;
		background: #fffdfa;
		font: inherit;
	}
</style>
