import { readdir, readFile, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const compiler = join(root, "node_modules/.bin/lightningcss");
// npm may block dependency install scripts. This script only places the
// already-installed platform binary at the CLI's expected location.
const setup = spawnSync(process.execPath, [join(root, "node_modules/lightningcss-cli/postinstall.js")], {
	stdio: "inherit",
});
if (setup.error) throw setup.error;
if (setup.status !== 0) throw new Error("Could not prepare lightningcss; run npm ci first.");

async function cssFiles(directory) {
	const entries = await readdir(directory, { withFileTypes: true });
	const files = await Promise.all(entries.map(async (entry) => {
		const path = join(directory, entry.name);
		return entry.isDirectory() ? cssFiles(path) : path.endsWith(".css") ? [path] : [];
	}));
	return files.flat().sort();
}

const files = await cssFiles(join(root, "source"));
const css = (await Promise.all(files.map((path) => readFile(path, "utf8")))).join("\n");
const result = spawnSync(compiler, ["--minify", "--browserslist"], {
	input: css,
	encoding: "utf8",
	cwd: root,
	env: { ...process.env, BROWSERSLIST: "chrome 108" },
	maxBuffer: 10 * 1024 * 1024,
});
if (result.error) throw result.error;
if (result.status !== 0) throw new Error(result.stderr || "CSS build failed");
const header = await readFile(join(root, "source/header.txt"), "utf8");
const settings = await readFile(join(root, "source/style-settings.yaml"), "utf8");
await writeFile(join(root, "theme.css"), `/*\n${header}*/\n${result.stdout}\n/* @settings\n${settings}*/\n`);
console.log(`Built theme.css from ${files.length} source files.`);
