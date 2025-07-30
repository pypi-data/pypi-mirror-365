<!-- index.svelte -->

<script lang="ts">
	// This component acts as a bridge between the Gradio Python backend and the Svelte UI.
	import BottomBarPanel from "./shared/BottomBarPanel.svelte";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import type { Gradio } from "@gradio/utils";
	import Column from "@gradio/column";
	
	export let open = true;
	export let loading_status: LoadingStatus;
	export let gradio: Gradio<{
		expand: never;
		collapse: never;
	}>;
	export let height: number | string;
	export let visible = true;
	export let bring_to_front = false;
</script>

<StatusTracker
	autoscroll={gradio.autoscroll}
	i18n={gradio.i18n}
	{...loading_status}
/>

{#if visible}
	<!-- Pass the new 'bring_to_front' prop to the panel component -->
	<BottomBarPanel
		bind:open
		{height}
		{bring_to_front}
		on:expand={() => gradio.dispatch("expand")}
		on:collapse={() => gradio.dispatch("collapse")}
	>
		<Column>
			<slot />
		</Column>
	</BottomBarPanel>
{/if}