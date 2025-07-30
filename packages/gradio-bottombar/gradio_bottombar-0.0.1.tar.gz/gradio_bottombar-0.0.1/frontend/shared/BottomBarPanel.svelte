<!-- shared/BottomBarPanel.svelte -->

<script lang="ts">
	import { createEventDispatcher, onMount } from "svelte";
	const dispatch = createEventDispatcher<{
		expand: void;
		collapse: void;
	}>();

	export let open = true;
	export let height: number | string;
	export let bring_to_front = false;

	// Using a temporary variable to animate the panel opening at the start.
	let mounted = false;
	let _open = false;

	let height_css = typeof height === "number" ? `${height}px` : height;
	let prefersReducedMotion: boolean;

	onMount(() => {
		mounted = true;
		const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
		prefersReducedMotion = mediaQuery.matches;

		const updateMotionPreference = (e: MediaQueryListEvent): void => {
			prefersReducedMotion = e.matches;
		};

		mediaQuery.addEventListener("change", updateMotionPreference);

		return () => {
			mediaQuery.removeEventListener("change", updateMotionPreference);
		};
	});

	$: if (mounted) _open = open;
</script>

<!-- Add a conditional class 'on-top' based on the bring_to_front prop -->
<div
	class="bottom-bar"
	class:open={_open}
	class:reduce-motion={prefersReducedMotion}
	class:on-top={bring_to_front}
	style="height: {height_css};"
>
	<button
		on:click={() => {
			_open = !_open;
			open = _open;
			if (_open) {
				dispatch("expand");
			} else {
				dispatch("collapse");
			}
		}}
		class="toggle-bottom-button"
		aria-label="Toggle Bottom Bar"
	>
		<div class="chevron">
			<span class="chevron-arrow"></span>
		</div>
	</button>
	<div class="bar-content">
		<slot />
	</div>
</div>

<style>
	.bottom-bar {
		display: flex;
		flex-direction: column;
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		width: 100%;
		background-color: var(--background-fill-secondary);
		transform: translateY(100%);
		/* The default z-index, which is the same level as sidebars. */
		z-index: 1000;
		border-top: 1px solid var(--border-color-primary);
		box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
	}

	/* This class is applied when bring_to_front is true. */
	.bottom-bar.on-top {
		/* Use a high z-index to ensure it's on top of other elements like sidebars. */
		z-index: 2000;
	}

	.bottom-bar:not(.reduce-motion) {
		transition: transform 0.3s ease-in-out;
	}

	.bottom-bar.open {
		transform: translateY(0);
	}

	.toggle-bottom-button {
		position: absolute;
		top: 0;
		left: 50%;
		transform: translate(-50%, -100%);
		background: var(--background-fill-secondary);
		border: 1px solid var(--border-color-primary);
		border-bottom: none;
		cursor: pointer;
		padding: var(--size-2);
		display: flex;
		align-items: center;
		justify-content: center;
		width: var(--size-10);
		height: var(--size-6);
		/* The button's z-index should be relative to its parent bar */
		z-index: inherit;
		border-radius: var(--radius-lg) var(--radius-lg) 0 0;
	}

	.toggle-bottom-button:not(.reduce-motion) {
		transition: all 0.3s ease-in-out;
	}

	.chevron {
		position: relative;
		display: block;
		width: var(--size-3);
		height: var(--size-3);
	}
		
	.chevron-arrow {
		position: absolute;
		box-sizing: border-box;		
		top: 10%;
		left: 18%;
		width: 80%;
		height: 80%;
		border-bottom: var(--size-0-5) solid var(--body-text-color);
		border-right: var(--size-0-5) solid var(--body-text-color);				
		transform: rotate(-135deg);
	}

	.bottom-bar:not(.reduce-motion) .chevron-arrow {		
		transition: transform 0.3s ease-in-out;
	}
	
	.bottom-bar.open .chevron-arrow {
		transform: rotate(45deg);
	}

	.bar-content {
		padding: var(--size-4);
		overflow-y: auto;
		flex-grow: 1;
	}

	.bar-content {
		padding: var(--size-4);
		overflow-y: auto;
		flex-grow: 1;
	}
</style>