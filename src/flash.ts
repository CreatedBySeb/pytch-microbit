import { readFile } from "node:fs/promises";
import process, { cwd, exit } from "node:process";
import { DAPLink, WebUSB as DAPWebUSB } from "dapjs";
import { WebUSB } from "usb";
import { BoardVersion, getBuildOutputDir, getHexPath } from "./shared";

const BOARD_VERSIONS: BoardVersion[] = [1, 2];
const DEVICE_FILTER: USBDeviceFilter = { vendorId: 0x0d28, productId: 0x0204 };
const POLL_INTERVAL = 1000;

type FilteredUSBDevice = USBDevice & { serialNumber: string };

/**
 * Information required across various functions
 */
interface Context {
    hexFiles: Buffer<ArrayBuffer>[];
    inflight: Promise<unknown>[];
    seenDevices: Set<string>;
    usb: WebUSB;
}

/**
 * Determines the major revision of a micro:bit board
 * @param serial The USB serial number (SERNO) for the board
 * @returns Either `1` or `2`, representing the major revision of the board
 */
function getBoardVersion(serial: string): BoardVersion {
    // Note: Based on https://support.microbit.org/support/solutions/articles/19000035697-what-are-the-usb-vid-pid-numbers-for-micro-bit
    return (serial.startsWith("9900") || serial.startsWith("9901")) ? 1 : 2;
}

/**
 * Attempts to flash the provided device with the correct hex file
 * @param context The program context, containing the hex files
 * @param device The device to flash
 */
async function flashDevice(context: Context, device: FilteredUSBDevice) {
    const version = getBoardVersion(device.serialNumber);
    console.log(`- Found new micro:bit V${version} board (${device.serialNumber}), attempting to flash...`);

    const transport = new DAPWebUSB(device);
    const dap = new DAPLink(transport);
    await dap.connect();

    const hex = context.hexFiles[version - 1];
    await dap.flash(hex);

    await dap.disconnect();
    console.log(`- Successfully flashed micro:bit V${version} board (${device.serialNumber})`);
}

/**
 * Polls for previously unseen devices and attempts to start flashing them
 * @param context The program context
 */
async function pollDevices(context: Context) {
    const devices = await context.usb.getDevices();
    const newDevices = devices.filter((d) => d.serialNumber && !context.seenDevices.has(d.serialNumber)) as FilteredUSBDevice[];

    if (!newDevices.length) return;
    context.inflight.push(...newDevices.map((d) => {
        context.seenDevices.add(d.serialNumber);
        return flashDevice(context, d);
    }));
}

async function main() {
	console.log("Running in " + cwd());
	console.log("Starting Pytch micro:bit flashing tool...");

    console.log("- Reading hex files...");
    const fwPath = getBuildOutputDir();
    const hexFiles = await Promise.all(BOARD_VERSIONS.map((v) => readFile(getHexPath(fwPath, v))));
    console.log("- Read in hex files from " + fwPath);

    console.log("- Initialising USB...");
    const usb = new WebUSB({ allowedDevices: [DEVICE_FILTER] });
    console.log("- USB initialised");

    let context: Context = { hexFiles, inflight: [], seenDevices: new Set(), usb };
    let interval: NodeJS.Timeout | null = null;

    process.on("SIGINT", () => {
        console.log("Caught SIGINT, stopping polling and allowing operations to finish...");
        if (interval !== null) clearInterval(interval);

        Promise.allSettled(context.inflight)
            .then(() => {
                console.log("All operations completed, exiting");
                exit();
            });
    });

    console.log("Starting polling loop, CTRL+C to exit...")
    interval = setInterval(() => pollDevices(context), POLL_INTERVAL);
}

if (require.main === module) {
    main();
}
