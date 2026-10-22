"""Check the installed theme/helper against Obsidian's actual editor parser.

Uses an isolated in-memory editor; no notes or workspace tabs are changed.
Run from any directory with Padua open: python scripts/verify-headings.py
"""

import json
import os
import subprocess
import tempfile
import time

cases = []
for level in range(1, 7):
    hashes = "#" * level
    for text in (f"{hashes} text", hashes, f"- {hashes} text", f"- {hashes}"):
        cases.append({"text": text, "level": level})
    cases.append({"text": f"- Parent\n\t- {hashes} ", "level": level, "line": 1})
cases += [
    {"text": "```markdown\n- ###\n```", "level": 0, "line": 1},
    {"text": "", "level": 0},
    {"text": "- Plain list", "level": 0},
    {"text": "- #######", "level": 0},
    {"text": "\t- ###", "level": 0},
    {"text": "1. ###", "level": 0},
    {"text": "---\nitems:\n- ###\n---", "level": 0, "line": 2},
]

code = r"""(() => {
const cases = CASES;
const cm = app.workspace.getMostRecentLeaf().view.editor.cm;
const fixture = document.createElement('div');
fixture.className = 'markdown-source-view is-live-preview';
fixture.style.cssText = 'position:absolute;left:-10000px;top:0;width:800px;height:10000px';
document.body.append(fixture);
let view;
const classes = document.body.className;
const failures = [];
try {
    document.body.classList.remove('no-heading-background', 'no-lp-heading-level-indicator');
    const labels = line => [
        getComputedStyle(line, '::before').content,
        getComputedStyle(line, '::after').content,
        ...[...line.querySelectorAll('.cm-header')].map(s => getComputedStyle(s, '::before').content)
    ].filter(s => /^"H[1-6]"$/.test(s));
    const check = (ok, message) => { if (!ok) failures.push(message); };
    for (let i = 0; i < cases.length; i++) {
        const sample = cases[i];
        const state = cm.state.update({
            changes: {from:0, to:cm.state.doc.length, insert:sample.text + '\nend'},
            selection: {anchor:sample.text.length + 4}
        }).state;
        if (view) view.setState(state);
        else view = new cm.constructor({state, parent:fixture});
        const target = sample.line ?? 0;
        for (const active of [false, true]) {
            view.dispatch({selection:{anchor:view.state.doc.line(active ? target + 1 : view.state.doc.lines).to}});
            const line = fixture.querySelectorAll('.cm-line')[target];
            const visible = line ? labels(line) : [];
            check(JSON.stringify(visible) === JSON.stringify(sample.level ? ['"H' + sample.level + '"'] : []),
                `line ${i + 1}, active=${active}: ${JSON.stringify(visible)} for ${sample.text}`);
            if (sample.level) {
                check(!!line, `missing rendered heading for case ${i + 1}`);
                if (!line) continue;
                check(getComputedStyle(line).borderTopStyle === 'solid', `missing border on line ${i + 1}`);
                check(getComputedStyle(line).backgroundColor !== 'rgba(0, 0, 0, 0)', `missing background on line ${i + 1}`);
            } else {
                check(!fixture.querySelector('.rice-empty-heading'), `non-heading decorated for case ${i + 1}`);
            }
        }
        document.body.classList.add('no-lp-heading-level-indicator', 'no-heading-background');
        for (const line of fixture.querySelectorAll('.rice-empty-heading')) {
            check(labels(line).length === 0, 'label visibility toggle ignored');
            check(getComputedStyle(line).borderTopStyle !== 'solid', 'background visibility toggle ignored');
        }
        document.body.classList.remove('no-lp-heading-level-indicator', 'no-heading-background');
    }
    return JSON.stringify({cases:cases.length, failures});
} finally {
    view?.destroy();
    fixture.remove();
    document.body.className = classes;
}
})()""".replace("CASES", json.dumps(cases, ensure_ascii=False))

# The CLI accepts a single-line JavaScript argument.
code = " ".join(code.splitlines())
code = "(()=>{try{return " + code + "}catch(error){return JSON.stringify({cases:0,failures:[String(error)]})}})()"
environment = {key: value for key, value in os.environ.items() if key != "ELECTRON_RUN_AS_NODE"}
with tempfile.NamedTemporaryFile(mode="w", suffix=".js", prefix="rice-heading-check-") as script:
    script.write(code)
    script.flush()
    # Keep the IPC argument short; long JavaScript arguments can be truncated.
    loader = f"window.__riceHeadingVerification=eval(require('fs').readFileSync({json.dumps(script.name)}, 'utf8'))"
    subprocess.run(
        ["obsidian", "vault=Padua", "eval", "code=" + loader],
        capture_output=True, text=True, env=environment, check=True,
    )
    output = None
    for _ in range(10):
        result = subprocess.run(
            ["obsidian", "vault=Padua", "eval", "code=window.__riceHeadingVerification"],
            capture_output=True, text=True, env=environment, check=True,
        )
        output = next((line[3:] for line in result.stdout.splitlines() if line.startswith("=> {")), None)
        if output is not None:
            break
        time.sleep(0.1)
    subprocess.run(
        ["obsidian", "vault=Padua", "eval", "code=delete window.__riceHeadingVerification"],
        capture_output=True, text=True, env=environment, check=True,
    )
if output is None:
    raise SystemExit(f"No verification result from Obsidian: {result.stdout}{result.stderr}")
report = json.loads(output)
if report["failures"]:
    raise SystemExit("\n".join(report["failures"]))
print(f"PASS: {report['cases']} parser cases in active/inactive states, including all heading levels, empty headings, nested lists, code/frontmatter exclusions, and visibility toggles.")
