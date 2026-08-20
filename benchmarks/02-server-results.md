# 02 - Serve: load test + saturation reading

Host `Darwin-arm64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=10` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 140 | 2.50 | 3000 | 4500 | 5000 | 7.7 | 0.0% |
| 50 | 144 | 2.45 | 19000 | 21000 | 22000 | 40.7 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **0.98x** (20% of linear) |
| P95 latency | **4.67x** |
| Effective concurrency at 50 users | 40.7 vs `--parallel 4` slots (occupancy/slot ratio 10.18) |

**Saturated.** Throughput delivered only 0.98x for 5x the offered load, and effective concurrency (40.7) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 0.98x while P95 moved 4.67x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

## Your reading

Server bão hòa hoàn toàn ở mức ~10-15 users với giới hạn cứng `--parallel 4`. Bằng chứng rõ ràng nhất là khi offered load tăng gấp 5 lần (từ 10 lên 50 users), Throughput thực tế (RPS) không hề tăng (2.50 -> 2.45 RPS, đạt 0.98x), trong khi độ trễ P95 tăng vọt 4.67x (từ 4.5s lên 21.0s).

Theo Định luật Little ($L = \lambda \times W$), Effective Concurrency tại 50 users lên tới 40.7, vượt xa 4 compute slots. Điều này chứng minh 80-90% độ trễ P95 (khoảng ~16.5s) là **Queue Time (thời gian chờ trong hàng đợi)** chứ không phải Compute Time.

Nếu đặt SLO P95 ≤ 5000ms, tại 50 users Goodput@SLO giảm về 0%. Để nâng Goodput@SLO, knob đầu tiên cần thay đổi là **tăng `--parallel` từ 4 lên 8 hoặc 12**, vì máy có 32 GB RAM và băng thông M1 Pro đủ sức gánh thêm batch slots song song, giải phóng hàng đợi và hạ queue time về ngưỡng chấp nhận được.

