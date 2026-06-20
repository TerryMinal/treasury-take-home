<script lang="ts">
	export let label = 'Upload label file';
	export let name = 'label-file';
	export let accept = '.png,.jpg,.jpeg,.txt';
	export let multiple = false;
	export let files: FileList | null = null;
</script>

<label class="field">
	<span>{label}</span>
	<input bind:files {accept} {multiple} name={name} type="file" />
</label>

<style>
	.field {
		display: grid;
		gap: 0.5rem;
		font-weight: 600;
	}

	input {
		border: 1px solid #b9b0a2;
		border-radius: 0.75rem;
		padding: 0.9rem;
		background: #fffdfa;
	}
</style>
