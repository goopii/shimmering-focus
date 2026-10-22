const { Plugin } = require("obsidian");
const { StateField, RangeSetBuilder } = require("@codemirror/state");
const { Decoration, EditorView } = require("@codemirror/view");
const { syntaxTree } = require("@codemirror/language");

// Match empty headings in bullet lists, including nested bullets.
const emptyHeading = /^[\t ]*[-+*][\t ]+(#{1,6})[\t ]*$/;

function decorations(state) {
	const builder = new RangeSetBuilder();
	const tree = syntaxTree(state);
	for (let number = 1; number <= state.doc.lines; number++) {
		const line = state.doc.line(number);
		const match = emptyHeading.exec(line.text);
		if (!match) continue;
		// Consult Obsidian's parser so code blocks and frontmatter stay unchanged.
		const marker = line.from + line.text.indexOf("#");
		let node = tree.resolveInner(marker, 1);
		let isHeading = false;
		for (; node; node = node.parent) {
			if (/header/i.test(node.name)) {
				isHeading = true;
				break;
			}
		}
		if (!isHeading) continue;
		builder.add(line.from, line.from, Decoration.line({
			attributes: {
				class: "rice-empty-heading",
				"data-rice-heading-label": `H${match[1].length}`,
			},
		}));
	}
	return builder.finish();
}

module.exports = class RiceThemeHelper extends Plugin {
	onload() {
		this.registerEditorExtension(StateField.define({
			create: decorations,
			update(value, transaction) {
				return transaction.docChanged || syntaxTree(transaction.startState) !== syntaxTree(transaction.state)
					? decorations(transaction.state) : value;
			},
			provide: (field) => EditorView.decorations.from(field),
		}));
	}
};
