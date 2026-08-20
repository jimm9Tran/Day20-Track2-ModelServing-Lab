# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Darwin-arm64` · llama.cpp `b10488`
CPU: **10 physical · 10 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 116.5 | 97% |
| 5 | 119.6 | 100% |
| 10 | 119.8 | 100% |
| 20 | 86.2 | 72% |

**Best**: `-t 10` at 119.8 tok/s
**Slowest tested**: `-t 20` at 86.2 tok/s (1.39x spread)
**Against the physical-core default** (`-t 10`, 119.8 tok/s): 1.00x

Use this in your run:

```bash
LAB_N_THREADS=10 make bench
```

## Your explanation

Điểm Knee nằm tại `-t 10` (119.8 tok/s), trùng khớp với số nhân vật lý (10 physical cores: 8 Performance cores + 2 Efficiency cores) của chip Apple M1 Pro.

1. **Từ 1 lên 10 threads:** Tốc độ decode tăng nhẹ từ 116.5 lên 119.8 tok/s. Do model Qwen3.5 0.8B có kích thước rất nhỏ (~0.5 GB) và giai đoạn decode là memory-bandwidth bound, chỉ với 1-5 threads trên kiến trúc Unified Memory (băng thông ~200 GB/s) hệ thống đã gần như bão hòa năng lực đọc weights.
2. **Tại `-t 20` (86.2 tok/s, giảm 28%):** Hệ thống rơi vào trạng thái **Thread Oversubscription** nghiêm trọng (20 threads cạnh tranh trên 10 cores). Việc ép 20 luồng gây ra:
   - Chi phí Context Switching và CPU scheduling overhead tăng cao.
   - Hiện tượng L2 Cache Contention / Thrashing và lock contention trong `llama.cpp`.
   - Các luồng bị kẹt trên 2 nhân tiết kiệm điện (E-cores) khiến barrier synchronization phải chờ luồng chậm nhất, làm tụt hiệu năng chung.

