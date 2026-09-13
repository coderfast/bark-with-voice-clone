"""
normalize_audio.py — LUFS Loudness Normalizer for Game Audio

Normalizes audio files to a consistent loudness level (LUFS) so that
3D spatialization works correctly across all sound assets.

Usage:
    # Single file
    python normalize_audio.py input.wav -o output.wav --target -14

    # Batch (folder)
    python normalize_audio.py --folder sounds/raw/ --output-folder sounds/normalized/ --target -14

    # Analyze only (no modification)
    python normalize_audio.py --folder sounds/raw/ --analyze-only

    # With report
    python normalize_audio.py --folder sounds/raw/ --report loudness_report.csv
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
import pyloudnorm as pyln


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".wav", ".flac", ".ogg", ".mp3", ".aiff", ".aif"}

LUFS_PRESETS = {
    "mobile": -14,
    "aaa": -16,
    "dialogue": -12,
    "sfx": -16,
    "music": -14,
    "quiet": -18,
}


# ---------------------------------------------------------------------------
# LoudnessAnalyzer
# ---------------------------------------------------------------------------

class LoudnessAnalyzer:
    """Measures integrated loudness (LUFS) and true peak."""

    @staticmethod
    def measure(audio: np.ndarray, sample_rate: int) -> dict:
        """
        Measure loudness metrics for an audio signal.

        Returns:
            dict with keys: lufs, true_peak_dbtp, duration_sec
        """
        duration = len(audio) / sample_rate

        if audio.size == 0 or np.max(np.abs(audio)) < 1e-10:
            return {
                "lufs": float("-inf"),
                "true_peak_dbtp": float("-inf"),
                "duration_sec": duration,
            }

        # Integrated loudness (LUFS)
        meter = pyln.Meter(sample_rate)
        lufs = meter.integrated_loudness(audio)

        # True peak (dBTP) — scan all samples
        peak = np.max(np.abs(audio))
        true_peak_dbtp = 20.0 * math.log10(peak) if peak > 0 else float("-inf")

        return {
            "lufs": lufs,
            "true_peak_dbtp": true_peak_dbtp,
            "duration_sec": round(duration, 3),
        }


# ---------------------------------------------------------------------------
# LoudnessNormalizer
# ---------------------------------------------------------------------------

class LoudnessNormalizer:
    """Normalizes audio to a target LUFS with true-peak limiting."""

    @staticmethod
    def normalize(
        audio: np.ndarray,
        sample_rate: int,
        target_lufs: float,
        true_peak_limit: float = -1.0,
    ) -> np.ndarray:
        """
        Normalize audio to target LUFS, applying soft limiting if needed.

        Args:
            audio: Input audio array (samples x channels).
            sample_rate: Sample rate in Hz.
            target_lufs: Desired integrated loudness in LUFS.
            true_peak_limit: Maximum true peak in dBTP.

        Returns:
            Normalized audio array.
        """
        if audio.size == 0 or np.max(np.abs(audio)) < 1e-10:
            return audio

        meter = pyln.Meter(sample_rate)
        current_lufs = meter.integrated_loudness(audio)

        if math.isinf(current_lufs):
            return audio

        # Normalize to target LUFS
        normalized = pyln.normalize.loudness(audio, current_lufs, target_lufs)

        # True-peak limiting
        peak = np.max(np.abs(normalized))
        peak_dbtp = 20.0 * math.log10(peak) if peak > 0 else float("-inf")

        if peak_dbtp > true_peak_limit:
            gain_reduction = true_peak_limit - peak_dbtp
            linear_limit = 10.0 ** (gain_reduction / 20.0)
            normalized = np.clip(normalized, -linear_limit, linear_limit)

        return normalized


# ---------------------------------------------------------------------------
# BatchProcessor
# ---------------------------------------------------------------------------

class BatchProcessor:
    """Processes multiple audio files with loudness report generation."""

    def __init__(
        self,
        target_lufs: float = -14.0,
        true_peak_limit: float = -1.0,
        output_format: Optional[str] = None,
        sample_rate: Optional[int] = None,
    ):
        self.target_lufs = target_lufs
        self.true_peak_limit = true_peak_limit
        self.output_format = output_format
        self.sample_rate = sample_rate

    def collect_files(
        self, input_path: Path, extensions: set, recursive: bool
    ) -> list[Path]:
        """Collect audio files from a path (file or folder)."""
        if input_path.is_file():
            if input_path.suffix.lower() in extensions:
                return [input_path]
            return []

        if not input_path.is_dir():
            return []

        pattern = "**/*" if recursive else "*"
        files = []
        for ext in extensions:
            files.extend(input_path.glob(f"{pattern}{ext}"))
            files.extend(input_path.glob(f"{pattern}{ext.upper()}"))
        return sorted(set(files))

    def process_file(self, filepath: Path, output_path: Path) -> dict:
        """Process a single audio file. Returns result dict."""
        result = {
            "filename": filepath.name,
            "original_lufs": None,
            "original_true_peak_dbtp": None,
            "normalized_lufs": None,
            "normalized_true_peak_dbtp": None,
            "gain_applied_db": None,
            "duration_sec": None,
            "sample_rate": None,
            "status": "error",
        }

        try:
            audio, sr = sf.read(filepath, dtype="float64")
            result["sample_rate"] = sr
        except Exception as e:
            result["status"] = f"read_error: {e}"
            return result

        # Measure original
        metrics = LoudnessAnalyzer.measure(audio, sr)
        result["original_lufs"] = round(metrics["lufs"], 2)
        result["original_true_peak_dbtp"] = round(metrics["true_peak_dbtp"], 2)
        result["duration_sec"] = metrics["duration_sec"]

        # Skip silent files
        if math.isinf(metrics["lufs"]):
            result["status"] = "skipped_silent"
            return result

        # Calculate gain
        gain = self.target_lufs - metrics["lufs"]
        result["gain_applied_db"] = round(gain, 2)

        # Normalize
        normalized = LoudnessNormalizer.normalize(
            audio, sr, self.target_lufs, self.true_peak_limit
        )

        # Measure normalized
        norm_metrics = LoudnessAnalyzer.measure(normalized, sr)
        result["normalized_lufs"] = round(norm_metrics["lufs"], 2)
        result["normalized_true_peak_dbtp"] = round(norm_metrics["true_peak_dbtp"], 2)

        # Save
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            out_sr = self.sample_rate or sr
            if out_sr != sr:
                import scipy.signal
                num_samples = int(len(normalized) * out_sr / sr)
                normalized = scipy.signal.resample(normalized, num_samples, axis=0)

            ext = self.output_format or filepath.suffix.lstrip(".")
            if not ext:
                ext = "wav"
            out_file = output_path.with_suffix(f".{ext}")

            subtype = None
            if ext.lower() == "wav":
                subtype = "PCM_16"

            sf.write(str(out_file), normalized, out_sr, subtype=subtype)
            result["status"] = "ok"
        except Exception as e:
            result["status"] = f"write_error: {e}"

        return result

    def process_batch(
        self,
        input_path: Path,
        output_path: Path,
        extensions: set,
        recursive: bool,
    ) -> list[dict]:
        """Process all files in a folder. Returns list of result dicts."""
        files = self.collect_files(input_path, extensions, recursive)
        if not files:
            print(f"No audio files found in: {input_path}")
            return []

        results = []
        total = len(files)
        print(f"Processing {total} file(s)...\n")

        for i, filepath in enumerate(files, 1):
            # Compute output path preserving relative structure
            try:
                rel = filepath.relative_to(input_path)
            except ValueError:
                rel = filepath.name
            out_file = output_path / rel

            print(f"  [{i}/{total}] {filepath.name}", end=" ... ")
            result = self.process_file(filepath, out_file)
            results.append(result)

            if result["status"] == "ok":
                orig = result["original_lufs"]
                norm = result["normalized_lufs"]
                gain = result["gain_applied_db"]
                print(f"{orig} -> {norm} LUFS (gain: {gain:+.1f} dB)")
            else:
                print(f"FAILED ({result['status']})")

        return results

    @staticmethod
    def generate_report(
        results: list[dict], output_path: str, fmt: Optional[str] = None
    ) -> None:
        """Generate a loudness report as CSV or JSON.

        If fmt is None, auto-detects from file extension (.json → json, else csv).
        """
        if not results:
            print("No results to report.")
            return

        # Auto-detect format from extension
        if fmt is None:
            ext = Path(output_path).suffix.lower()
            fmt = "json" if ext == ".json" else "csv"

        if fmt == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            fieldnames = [
                "filename",
                "original_lufs",
                "original_true_peak_dbtp",
                "normalized_lufs",
                "normalized_true_peak_dbtp",
                "gain_applied_db",
                "duration_sec",
                "sample_rate",
                "status",
            ]
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

        print(f"\nReport saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize audio files to a consistent LUFS loudness level.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
LUFS presets (use with --target):
  mobile    -14 LUFS  (mobile / casual games)
  aaa       -16 LUFS  (AAA / PC games)
  dialogue  -12 LUFS  (voice / dialogue)
  sfx       -16 LUFS  (sound effects)
  music     -14 LUFS  (background music)
  quiet     -18 LUFS  (ambient / atmosphere)

Examples:
  %(prog)s input.wav -o output.wav --target -14
  %(prog)s --folder sounds/raw/ --output-folder sounds/normalized/ --target -14
  %(prog)s --folder sounds/raw/ --analyze-only --report analysis.csv
  %(prog)s --folder sounds/raw/ --output-folder out/ --report report.csv --format wav
        """,
    )

    # Input
    parser.add_argument(
        "input",
        nargs="?",
        help="Input audio file path",
    )
    parser.add_argument(
        "--folder",
        help="Input folder to process all audio files",
    )

    # Output
    parser.add_argument(
        "-o", "--output",
        help="Output file path (single file mode)",
    )
    parser.add_argument(
        "--output-folder",
        help="Output folder (batch mode)",
    )

    # Normalization
    parser.add_argument(
        "--target",
        default="-14",
        help="Target LUFS: number (-24 to -6) or preset (mobile, aaa, dialogue, sfx, music, quiet). Default: -14",
    )
    parser.add_argument(
        "--true-peak",
        type=float,
        default=-1.0,
        help="True peak limit in dBTP (default: -1.0)",
    )

    # Modes
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze loudness, do not normalize",
    )
    parser.add_argument(
        "--report",
        metavar="PATH",
        help="Save loudness report (.csv or .json, auto-detected from extension)",
    )

    # Format options
    parser.add_argument(
        "--format",
        choices=["wav", "flac", "ogg", "aiff"],
        help="Output format (default: same as input)",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        help="Output sample rate in Hz (default: same as input)",
    )

    # Batch options
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subfolders recursively",
    )
    parser.add_argument(
        "--extensions",
        default=".wav,.flac,.ogg,.mp3",
        help="Comma-separated file extensions to process (default: .wav,.flac,.ogg,.mp3)",
    )

    return parser


def resolve_lufs_target(value: str) -> float:
    """Resolve a LUFS value from preset name or numeric string."""
    preset = value.lower().strip()
    if preset in LUFS_PRESETS:
        return LUFS_PRESETS[preset]
    try:
        target = float(value)
        if not (-24 <= target <= -6):
            print(f"Warning: Target {target} LUFS is outside recommended range (-24 to -6)")
        return target
    except ValueError:
        print(f"Error: Invalid target '{value}'. Use a number (-24 to -6) or preset: {', '.join(LUFS_PRESETS.keys())}")
        sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Validate input
    if not args.input and not args.folder:
        parser.error("Provide either an input file or --folder")

    target = resolve_lufs_target(str(args.target))
    extensions = {e.strip() for e in args.extensions.split(",")}
    for ext in list(extensions):
        if not ext.startswith("."):
            extensions.discard(ext)
            extensions.add(f".{ext}")

    # Single file mode
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            sys.exit(1)

        if args.analyze_only:
            try:
                audio, sr = sf.read(str(input_path), dtype="float64")
            except Exception as e:
                print(f"Error reading {input_path}: {e}")
                sys.exit(1)

            metrics = LoudnessAnalyzer.measure(audio, sr)
            print(f"\nFile:      {input_path.name}")
            print(f"LUFS:      {metrics['lufs']:.1f}")
            print(f"True Peak: {metrics['true_peak_dbtp']:.1f} dBTP")
            print(f"Duration:  {metrics['duration_sec']:.2f}s")
            print(f"Rate:      {sr} Hz")

            if args.report:
                result = {
                    "filename": input_path.name,
                    "original_lufs": round(metrics["lufs"], 2),
                    "original_true_peak_dbtp": round(metrics["true_peak_dbtp"], 2),
                    "normalized_lufs": None,
                    "normalized_true_peak_dbtp": None,
                    "gain_applied_db": None,
                    "duration_sec": metrics["duration_sec"],
                    "sample_rate": sr,
                    "status": "analyzed",
                }
                BatchProcessor.generate_report([result], args.report)
            return

        output_path = Path(args.output) if args.output else input_path.with_name(
            f"{input_path.stem}_normalized{input_path.suffix}"
        )

        bp = BatchProcessor(
            target_lufs=target,
            true_peak_limit=args.true_peak,
            output_format=args.format,
            sample_rate=args.sample_rate,
        )

        print(f"Input:    {input_path}")
        print(f"Output:   {output_path}")
        print(f"Target:   {target} LUFS\n")

        result = bp.process_file(input_path, output_path)
        if result["status"] == "ok":
            print(f"  Original:  {result['original_lufs']} LUFS ({result['original_true_peak_dbtp']} dBTP)")
            print(f"  Normalized: {result['normalized_lufs']} LUFS ({result['normalized_true_peak_dbtp']} dBTP)")
            print(f"  Gain:       {result['gain_applied_db']:+.1f} dB")
            print(f"\nSaved to: {output_path}")
        else:
            print(f"  Error: {result['status']}")
            sys.exit(1)

        if args.report:
            BatchProcessor.generate_report([result], args.report)
        return

    # Batch mode
    input_folder = Path(args.folder)
    if not input_folder.exists():
        print(f"Error: Folder not found: {input_folder}")
        sys.exit(1)

    output_folder = Path(args.output_folder) if args.output_folder else input_folder.parent / f"{input_folder.name}_normalized"

    bp = BatchProcessor(
        target_lufs=target,
        true_peak_limit=args.true_peak,
        output_format=args.format,
        sample_rate=args.sample_rate,
    )

    print(f"Input:     {input_folder}")
    print(f"Output:    {output_folder}")
    print(f"Target:    {target} LUFS")
    print(f"Recursive: {'Yes' if args.recursive else 'No'}")
    print(f"Extensions: {', '.join(sorted(extensions))}\n")

    if args.analyze_only:
        files = bp.collect_files(input_folder, extensions, args.recursive)
        if not files:
            print("No audio files found.")
            sys.exit(0)

        print(f"Analyzing {len(files)} file(s)...\n")
        results = []
        for i, fp in enumerate(files, 1):
            try:
                audio, sr = sf.read(str(fp), dtype="float64")
                metrics = LoudnessAnalyzer.measure(audio, sr)
                result = {
                    "filename": fp.name,
                    "original_lufs": round(metrics["lufs"], 2),
                    "original_true_peak_dbtp": round(metrics["true_peak_dbtp"], 2),
                    "normalized_lufs": None,
                    "normalized_true_peak_dbtp": None,
                    "gain_applied_db": None,
                    "duration_sec": metrics["duration_sec"],
                    "sample_rate": sr,
                    "status": "analyzed",
                }
            except Exception as e:
                result = {
                    "filename": fp.name,
                    "original_lufs": None,
                    "original_true_peak_dbtp": None,
                    "normalized_lufs": None,
                    "normalized_true_peak_dbtp": None,
                    "gain_applied_db": None,
                    "duration_sec": None,
                    "sample_rate": None,
                    "status": f"error: {e}",
                }
            results.append(result)
            lufs_str = f"{result['original_lufs']:.1f}" if result["original_lufs"] is not None else "N/A"
            peak_str = f"{result['original_true_peak_dbtp']:.1f}" if result["original_true_peak_dbtp"] is not None else "N/A"
            print(f"  [{i}/{len(files)}] {fp.name}: {lufs_str} LUFS, {peak_str} dBTP")

        if args.report:
            BatchProcessor.generate_report(results, args.report)

        # Summary
        valid = [r for r in results if r["original_lufs"] is not None and not math.isinf(r["original_lufs"])]
        if valid:
            lufs_values = [r["original_lufs"] for r in valid]
            print(f"\nSummary:")
            print(f"  Files analyzed: {len(valid)}")
            print(f"  LUFS range:     {min(lufs_values):.1f} to {max(lufs_values):.1f}")
            print(f"  LUFS spread:    {max(lufs_values) - min(lufs_values):.1f} dB")
            print(f"  Target:         {target} LUFS")
        return

    # Batch normalize
    results = bp.process_batch(input_folder, output_folder, extensions, args.recursive)

    if results:
        ok_results = [r for r in results if r["status"] == "ok"]
        err_results = [r for r in results if r["status"] != "ok"]

        print(f"\n{'='*50}")
        print(f"Processed: {len(results)} files")
        print(f"  OK:      {len(ok_results)}")
        print(f"  Errors:  {len(err_results)}")

        if ok_results:
            gains = [r["gain_applied_db"] for r in ok_results if r["gain_applied_db"] is not None]
            if gains:
                print(f"  Gain range: {min(gains):+.1f} to {max(gains):+.1f} dB")

        if args.report:
            BatchProcessor.generate_report(results, args.report)


if __name__ == "__main__":
    main()
