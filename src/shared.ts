import { resolve } from "node:path";
import { cwd } from "node:process";

export type BoardVersion = 1 | 2;

/**
 * Get the path to the firmware build output dir
 * @returns The output dir as a string path
 */
export function getBuildOutputDir(): string {
    return resolve(cwd(), "build");
}


/**
 * Get the path to a hex file based on the board version
 * @param hexDir The path to the dir containing the hex files, see {@link getBuildOutputDir}
 * @param version The targetted board version
 */
export function getHexPath(hexDir: string, version: BoardVersion): string {
    return resolve(hexDir, `pytch-microbit-v${version}.hex`);
}
