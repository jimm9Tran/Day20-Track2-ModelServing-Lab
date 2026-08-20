# 02 - Continuous batching under load (u50)

Host `Darwin-arm64` · `--parallel 4` · 30 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.84 of 4 slots (96%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 17683 |

Highest sampled value was **3.84 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## Your observation

Đỉnh batch width ghi nhận được là **3.84 / 4 slots (96%)**, đồng thời `requests_processing` đạt tối đa 4/4 và `requests_deferred` lên tới 46.

Con số 3.84 hoàn toàn phù hợp và bổ trợ chặt chẽ cho con số Effective Concurrency (40.7):
- `n_busy_slots_per_decode` (3.84) phản ánh số slot thực tế đang cùng tính toán trong mỗi vòng lặp decode (bị chặn trên bởi `--parallel 4`), chứng minh scheduler của `llama.cpp` đã pack gần như tối đa các request song song vào continuous batching.
- `Effective concurrency` (40.7) tính toàn bộ request trong hệ thống (4 request đang tính toán + ~37 request đang xếp hàng chờ). Tôi tin cậy cả hai vì mỗi chỉ số đo một khía cạnh: một bên đo Compute Slot Saturation và một bên đo System Queue Congestion.

