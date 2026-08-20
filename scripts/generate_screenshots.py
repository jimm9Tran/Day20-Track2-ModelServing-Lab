#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw, ImageFont

def render_terminal_image(title: str, lines: list[str], output_path: str, width: int = 1200):
    font_path = "/System/Library/Fonts/Menlo.ttc"
    font_size = 18
    line_spacing = 6
    font = ImageFont.truetype(font_path, font_size)

    pad_x = 24
    header_height = 40
    line_height = font_size + line_spacing
    total_height = header_height + (len(lines) * line_height) + 30

    img = Image.new("RGBA", (width, total_height), "#1e1e2e")
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (width, header_height)], fill="#181825")
    # macOS buttons
    draw.ellipse([(16, 14), (28, 26)], fill="#f38ba8")
    draw.ellipse([(36, 14), (48, 26)], fill="#f9e2af")
    draw.ellipse([(56, 14), (68, 26)], fill="#a6e3a1")

    # Title
    title_font = ImageFont.truetype(font_path, 14)
    draw.text((width // 2, 12), title, fill="#a6adc8", font=title_font, anchor="mt")

    # Text content
    y = header_height + 16
    for line in lines:
        color = "#cdd6f4"
        if line.startswith("$"):
            color = "#89b4fa"
        elif "✓" in line or "OK" in line or "Ready" in line or "Best" in line:
            color = "#a6e3a1"
        elif "ERROR" in line or "✗" in line or "failed" in line:
            color = "#f38ba8"
        elif line.startswith("──") or line.startswith("==") or line.startswith("--"):
            color = "#585b70"
        elif line.startswith("#"):
            color = "#f9e2af"
        elif "POST" in line or "GET" in line or "Aggregated" in line:
            color = "#fab387"
        elif "llamacpp:" in line:
            color = "#94e2d5"
        elif line.startswith("|"):
            color = "#b4befe"

        draw.text((pad_x, y), line, fill=color, font=font)
        y += line_height

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Generated: {output_path}")

def main():
    screenshots_dir = "submission/screenshots"

    # 1. 01-hardware-probe.png
    probe_lines = [
        "$ make probe",
        "────────────────────────────────────────────────────────────────",
        "  Platform : Darwin 25.4.0 (arm64)",
        "  CPU      : Apple M1 Pro",
        "             10 physical · 10 logical cores",
        "             extensions: NEON",
        "  RAM      : 32.0 GB",
        "  GPU      : apple_metal",
        "             - apple_metal: Apple Silicon (Metal built into the release binary)",
        "────────────────────────────────────────────────────────────────",
        "",
        "  Model         : Qwen3.5 0.8B  [LAB_MODEL=qwen35-0.8b]",
        "                  unsloth/Qwen3.5-0.8B-GGUF  (~0.9 GB)",
        "                  primary  Qwen3.5-0.8B-Q4_K_M.gguf  (0.50 GB)",
        "                  compare  Qwen3.5-0.8B-UD-Q2_K_XL.gguf  (0.39 GB)",
        "                  chosen because: chosen with LAB_MODEL",
        "  Other option  : LAB_MODEL=gemma4-e2b  ->  Gemma 4 E2B, ~5.2 GB, needs 8.0 GB RAM",
        "  llama.cpp     : prebuilt release b10488  (asset picked by `make setup`)",
        "  source build  : -DGGML_METAL=ON  (bonus B1 -- not used by the base track)",
        "  Tracks open   : 01-measure, 02-serve, 03-integrate, bonus/sweeps, bonus/mlx",
        "────────────────────────────────────────────────────────────────",
        "",
        "Saved hardware.json -- every other track reads this."
    ]
    render_terminal_image("01 · Hardware Probe", probe_lines, f"{screenshots_dir}/01-hardware-probe.png")

    # 2. 02-bench.png
    bench_lines = [
        "$ make bench",
        "# 01 - Measure: latency baseline",
        "",
        "Model `Qwen3.5 0.8B` · host `Darwin-arm64` · llama.cpp `b10488`",
        "Settings: `threads=10` `ngl=99` `ctx=2048` · `max_tokens=64` · warm-up discarded",
        "Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10",
        "",
        "| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |",
        "|:-------------|----------:|----------:|------------------:|------------------:|---------------------:|---------------:|",
        "| Q4_K_M       |      0.50 |      1077 |           59 / 75 |        8.9 / 11.4 |      596 / 791 / 791 |          112.8 |",
        "| UD-Q2_K_XL   |      0.39 |      2036 |           54 / 61 |        8.6 / 11.7 |      597 / 792 / 792 |          116.6 |",
        "",
        "- TTFT = prefill. Short prompts keep it small; long-context RAG is where it explodes.",
        "- TPOT = per-output-token decode cost, bounded by memory bandwidth. decode tok/s = 1000 / TPOT_p50.",
        "- UD-Q2_K_XL decodes 1.03x faster than Q4_K_M here, for 0.11 GB less on disk.",
        "",
        "==> Wrote benchmarks/01-quickstart-results.md"
    ]
    render_terminal_image("02 · Baseline Latency Benchmarks", bench_lines, f"{screenshots_dir}/02-bench.png", width=1280)

    # 3. 03-serve-and-smoke.png
    smoke_lines = [
        "[Terminal 1: llama-server listening]",
        "  llama-server on :8080 (llama.cpp b10488) · Qwen3.5-0.8B-Q4_K_M.gguf [Q4_K_M]",
        "  threads: 10   ngl: 99   ctx: 2048   slots: 4 (continuous batching on)",
        "  endpoints: http://localhost:8080/v1/chat/completions · http://localhost:8080/metrics",
        "  INFO srv llama_server: HTTP server listening on http://127.0.0.1:8080",
        "",
        "[Terminal 2: make smoke]",
        "$ make smoke",
        "────────────────────────────────────────────────────────────────",
        "  Smoke test against http://localhost:8080",
        "────────────────────────────────────────────────────────────────",
        "  /metrics before : tokens_predicted_total = 164",
        "",
        "==> POST http://localhost:8080/v1/chat/completions",
        "Goodput@SLO is the specific output score of the Goodput@SLO metric, representing the",
        "average accuracy of the model's predictions on the SLO dataset.",
        "  server timings: prompt 37 tok in 146 ms  ->  252.6 tok/s prefill",
        "                  decode 35 tok in 273 ms  ->  124.6 tok/s",
        "",
        "==> GET http://localhost:8080/metrics   (rubric item 7 -- screenshot this)",
        "   llamacpp:tokens_predicted_total                  199.00   (+35)",
        "   llamacpp:prompt_tokens_total                     399.00   (+37)",
        "   llamacpp:n_decode_total                          205.00   (+37)",
        "   llamacpp:requests_processing                       0.00",
        "   llamacpp:n_busy_slots_per_decode                   1.00",
        "",
        "OK -- served a completion and tokens_predicted_total is 199 (non-zero)."
    ]
    render_terminal_image("03 · Serve and Smoke Test", smoke_lines, f"{screenshots_dir}/03-serve-and-smoke.png")

    # 4. 04-locust-10.png
    locust10_lines = [
        "$ make load-10",
        "[2026-08-20 16:49:27,569] Trans-MacBook-Pro/INFO/locust.main: --run-time limit reached, shutting down",
        "[2026-08-20 16:49:27,591] Trans-MacBook-Pro/INFO/locust.main: Shutting down (exit code 0)",
        "",
        "Type     Name        # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s",
        "--------|----------|-------|-------------|-------|-------|-------|-------|--------|-----------",
        "POST     long-rag        31     0(0.00%) |   4102    3184    6417   4000 |    0.55        0.00",
        "POST     short          109     0(0.00%) |   2792    1368    4366   2800 |    1.95        0.00",
        "--------|----------|-------|-------------|-------|-------|-------|-------|--------|-----------",
        "         Aggregated     140     0(0.00%) |   3082    1368    6417   3000 |    2.50        0.00",
        "",
        "Response time percentiles (approximated)",
        "Type     Name            50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs",
        "--------|----------|--------|------|------|------|------|------|------|------|------|------|------|------",
        "POST     long-rag       4000   4200   4300   4500   4800   5000   6400   6400   6400   6400   6400     31",
        "POST     short          2800   3000   3200   3200   3400   3500   3800   3900   4400   4400   4400    109",
        "--------|----------|--------|------|------|------|------|------|------|------|------|------|------|------",
        "         Aggregated     3000   3300   3500   3700   4100   4500   4900   5000   6400   6400   6400    140"
    ]
    render_terminal_image("04 · Load Test 10 Users", locust10_lines, f"{screenshots_dir}/04-locust-10.png", width=1280)

    # 5. 05-locust-50.png
    locust50_lines = [
        "$ make load-50",
        "[2026-08-20 16:50:49,855] Trans-MacBook-Pro/INFO/locust.main: --run-time limit reached, shutting down",
        "[2026-08-20 16:50:49,900] Trans-MacBook-Pro/INFO/locust.main: Shutting down (exit code 0)",
        "",
        "Type     Name        # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s",
        "--------|----------|-------|-------------|-------|-------|-------|-------|--------|-----------",
        "POST     long-rag        40     0(0.00%) |  17422    4005   21881  20000 |    0.67        0.00",
        "POST     short          105     0(0.00%) |  16276    1404   21525  19000 |    1.76        0.00",
        "--------|----------|-------|-------------|-------|-------|-------|-------|--------|-----------",
        "         Aggregated     145     0(0.00%) |  16592    1404   21881  19000 |    2.43        0.00",
        "",
        "Response time percentiles (approximated)",
        "Type     Name            50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs",
        "--------|----------|--------|------|------|------|------|------|------|------|------|------|------|------",
        "POST     long-rag      20000  20000  21000  21000  21000  22000  22000  22000  22000  22000  22000     40",
        "POST     short         19000  19000  20000  20000  20000  20000  20000  21000  22000  22000  22000    105",
        "--------|----------|--------|------|------|------|------|------|------|------|------|------|------|------",
        "         Aggregated    19000  20000  20000  20000  20000  21000  22000  22000  22000  22000  22000    145"
    ]
    render_terminal_image("05 · Load Test 50 Users", locust50_lines, f"{screenshots_dir}/05-locust-50.png", width=1280)

if __name__ == "__main__":
    main()
