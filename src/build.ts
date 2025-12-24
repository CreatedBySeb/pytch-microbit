import { MicropythonFsHex } from "@microbit/microbit-fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { cwd } from "node:process";
import { BoardVersion, getBuildOutputDir, getHexPath } from "./shared";

const V1_REPO = "bbcmicrobit/micropython";
const V2_REPO = "microbit-foundation/micropython-microbit-v2";

/**
 * Downloads the first artifact from the latest release of a GitHub repository as a string
 * @param repo A GitHub repository to fetch from
 * @returns The artifact represented as a string
 */
async function downloadLatestRelease(repo: string): Promise<string> {
	const releaseData = await fetch(`https://api.github.com/repos/${repo}/releases/latest`)
		.then((r) => r.json());

	// Note: This relies on the hex file being the only/first artifact, which is currently true
	const artifactData = await fetch(releaseData.assets[0].browser_download_url)
		.then((r) => r.text());

	return artifactData;
}

async function main() {
	console.log("Running in " + cwd())
	console.log("Building micro:bit hex files for Pytch...")

	console.log("- Reading Python files...");
	const paths = ["pytch", "microbit_v1", "microbit_v2"].map((p) => resolve(cwd(), p + ".py"));
	const [base, v1Py, v2Py] = await Promise.all(paths.map((p) => readFile(p)));
	console.log("- Read base, V1 and V2 Python files");

	console.log("- Fetching MicroPython firmware...");
	const [v1Firmware, v2Firmware] = await Promise.all([V1_REPO, V2_REPO].map(downloadLatestRelease));
	console.log("- Downloaded firmware for V1 and V2 boards");

	console.log("- Assembling hex files...");
	const fileSets = [[v1Firmware, v1Py], [v2Firmware, v2Py]] as const;
	const [v1Hex, v2Hex] = fileSets.map(([fw, py]) => {
		const fs = new MicropythonFsHex(fw);
		fs.write("pytch.py", base); // Always include common code
		fs.write("main.py", py); // Make board-specific file the entrypoint
		return fs.getIntelHex();
	});
	console.log("- Assembled hex files for V1 and V2 boards");

	console.log("- Writing hex files to disk...");
	const outPath = getBuildOutputDir();
	await mkdir(outPath, { recursive: true }); // Ensure output dir exists
	await Promise.all([v1Hex, v2Hex].map((hex, i) => {
		return writeFile(getHexPath(outPath, i + 1 as BoardVersion), hex);
	}));
	console.log("- Wrote hex files to " + outPath);

	console.log("Build completed successfully");
}

if (require.main === module) {
	main();
}
