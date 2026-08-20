# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Darwin-arm64` · llama.cpp `b10488`
Settings: `threads=10` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 1077 | 59 / 75 | 8.9 / 11.4 | 596 / 791 / 791 | 112.8 |
| UD-Q2_K_XL | 0.39 | 2036 | 54 / 61 | 8.6 / 11.7 | 597 / 792 / 792 | 116.6 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.03x faster** than `Q4_K_M` here, for 0.11 GB less on disk.

## Your observation

Trên Apple M1 Pro (Unified Memory bandwidth ~200 GB/s), bản 2-bit `UD-Q2_K_XL` (0.39 GB) giảm 22% dung lượng đĩa so với `Q4_K_M` (0.50 GB) và giúp tốc độ decode tăng nhẹ 1.03x (từ 112.8 lên 116.6 tok/s), TTFT P50 giảm từ 59ms xuống 54ms do kích thước weights cần load qua memory bus nhỏ hơn.

Tuy nhiên, với model kích thước nhỏ như Qwen3.5 0.8B, quantization xuống 2-bit gây suy giảm chất lượng sinh văn bản (coherence và reasoning) đáng kể, trong khi mức tăng tốc độ 3.4% là không đáng kể trên phần cứng có băng thông bộ nhớ lớn như Apple Silicon. Vì vậy, trên máy có đủ RAM, giữ mức `Q4_K_M` là lựa chọn tối ưu hơn nhiều để đảm bảo chất lượng phản hồi.

