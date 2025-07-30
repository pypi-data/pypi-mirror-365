<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { BlockTitle } from "@gradio/atoms";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { onMount, onDestroy } from "svelte";
	import { Editor } from "@tiptap/core";
	import StarterKit from "@tiptap/starter-kit";

	export let gradio: Gradio<{
		change: never;
		submit: never;
		input: never;
		clear_status: LoadingStatus;
	}>;
	export let label = "Textbox";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value = "";
	export let show_label: boolean;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus | undefined = undefined;
	export let value_is_output = false;
	export let interactive: boolean;
	export let rtl = false;

	let element: HTMLElement;
	let editor: Editor;
	let handleKeyDown: (event: KeyboardEvent) => void;
	const container = true;

	onMount(() => {
		editor = new Editor({
			element,
			extensions: [
				StarterKit.configure({
					// Configure list behavior
					bulletList: {
						keepMarks: true,
						keepAttributes: false,
					},
					orderedList: {
						keepMarks: true,
						keepAttributes: false,
					},
					// Disable code blocks since we just want simple text editing
					codeBlock: false,
					// Configure Enter behavior
					hardBreak: {
						keepMarks: false,
					}
				}),
			],
			content: value,
			editable: interactive,
			onUpdate: ({ editor }) => {
				// Get HTML content to preserve list formatting
				// Change to editor.getText() if you only want plain text without HTML tags
				value = editor.getHTML();
				gradio.dispatch("change");
				if (!value_is_output) {
					gradio.dispatch("input");
				}
			},
			editorProps: {
				attributes: {
					dir: rtl ? "rtl" : "ltr",
					"data-testid": "textbox",
					role: "textbox",
					"aria-label": label,
				},
			},
		});

		// Override Enter behavior - by default Tiptap will create new paragraphs/list items
		// If you want Shift+Enter to submit instead of creating a line break:
		handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Enter' && (event.shiftKey || event.ctrlKey || event.metaKey)) {
				event.preventDefault();
				gradio.dispatch("submit");
			}
		};
		
		element.addEventListener('keydown', handleKeyDown);
	});

	onDestroy(() => {
		if (handleKeyDown && element) {
			element.removeEventListener('keydown', handleKeyDown);
		}
		if (editor) {
			editor.destroy();
		}
	});

	// Keep external updates in sync
	$: if (editor && value !== editor.getHTML()) {
		editor.commands.setContent(value);
	}

	$: if (value === null) value = "";

	// Update editor editability when interactive prop changes
	$: if (editor) {
		editor.setEditable(interactive);
	}
</script>

<Block
	{visible}
	{elem_id}
	{elem_classes}
	{scale}
	{min_width}
	allow_overflow={false}
	padding={true}
>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
			on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
		/>
	{/if}

	<div class:container>
		<BlockTitle {show_label} info={undefined}>{label}</BlockTitle>

		<div
			bind:this={element}
			class="editor scroll-hide"
		/>
	</div>
</Block>

<style>
	.container {
		display: block;
		width: 100%;
	}

	.editor {
		display: block;
		position: relative;
		width: 100%;
	}

	/* Tiptap editor container styles */
	.editor :global(.ProseMirror) {
		outline: none !important;
		box-shadow: var(--input-shadow);
		background: var(--input-background-fill);
		padding: var(--input-padding);
		color: var(--body-text-color);
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		min-height: 5em;
		max-height: 20em;
		overflow-y: auto;
	}

	.container > .editor :global(.ProseMirror) {
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
	}

	.editor :global(.ProseMirror[contenteditable="false"]) {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.editor :global(.ProseMirror:focus) {
		box-shadow: var(--input-shadow-focus);
		border-color: var(--input-border-color-focus);
	}

	/* List styling */
	.editor :global(.ProseMirror ul),
	.editor :global(.ProseMirror ol) {
		padding-left: 1.5em;
		margin: 0.5em 0;
	}

	.editor :global(.ProseMirror li) {
		margin: 0.2em 0;
	}

	/* Paragraph styling */
	.editor :global(.ProseMirror p) {
		margin: 0.5em 0;
	}

	.editor :global(.ProseMirror p:first-child) {
		margin-top: 0;
	}

	.editor :global(.ProseMirror p:last-child) {
		margin-bottom: 0;
	}
</style>
