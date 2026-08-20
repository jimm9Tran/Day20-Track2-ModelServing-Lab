# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Trần Minh Hiền
**Cohort:** Cohort 4
**Ngày submit:** 2026-08-20

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** macOS 25.4.0 (Darwin arm64)
- **CPU:** Apple M1 Pro
- **Cores:** 10 physical / 10 logical
- **CPU extensions:** NEON
- **RAM:** 32.0 GB
- **Accelerator:** Apple Metal
- **llama.cpp asset đã tải:** llama-b10488-bin-macos-arm64.tar.gz
- **Model đã dùng:** Qwen3.5 0.8B (`LAB_MODEL=qwen35-0.8b`)
- **Quantization:** Q4_K_M + UD-Q2_K_XL (từ `models/active.json`)

**Chạy ở đâu:** laptop của tôi

**Setup story** (≤ 80 chữ): Setup tự động hoàn toàn qua Makefile. Tôi chọn `LAB_MODEL=qwen35-0.8b` để tải model Qwen3.5 0.8B (0.9 GB) thay vì bản 5.2 GB giúp tăng tốc độ benchmark. Prebuilt binary `llama.cpp` b10488 kích hoạt Apple Metal native mượt mà không gặp lỗi.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 1077 | 59 / 75 | 8.9 / 11.4 | 596 / 791 / 791 | 112.8 |
| UD-Q2_K_XL | 0.39 | 2036 | 54 / 61 | 8.6 / 11.7 | 597 / 792 / 792 | 116.6 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn 1.03x (116.6 vs 112.8 tok/s) và nhẹ hơn 22%. Tuy nhiên không đáng dùng vì trên M1 Pro tốc độ 4-bit đã rất cao, trong khi 2-bit làm giảm rõ rệt độ mạch lạc của câu trả lời.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 2.50 | 3000 | 4500 | 5000 | 7.7 | 0.0% |
| 50 | 2.45 | 19000 | 21000 | 22000 | 40.7 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 0.98×
- **P95 tăng:** 4.67×
- **Effective concurrency ở 50 users:** 40.7 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.84 / 4 slots

**Saturation reading** (≤ 80 chữ): Server bão hòa ở ~10-15 users. Bằng chứng là RPS giữ nguyên ở ~2.45 req/s trong khi P95 phồng 4.67x lên 21s. Effective concurrency 40.7 chứng minh ~80% latency là Queue Time chờ slot rảnh. Để nâng goodput@SLO (SLO 5s), tôi sẽ tăng `--parallel` lên 8 hoặc 12 slots vì máy còn dư nhiều RAM.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Localhost environment | stub |
| N17 Data pipeline | In-memory document list | stub |
| N18 Lakehouse | Dict TOY_DOCS | stub |
| N19 Vector + features | Keyword overlap retrieval | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 908.0 ms
- **stage chiếm nhiều nhất:** llm (100.0% của total)

**Reflection** (≤ 60 chữ): Khâu LLM chiếm 100% thời gian đúng như kỳ vọng vì retrieval là in-memory. Để giảm 2x độ trễ, tôi sẽ dùng Prompt Caching tái sử dụng context KV cache và giới hạn max output tokens.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Cấu hình số threads CPU đúng bằng số nhân vật lý (-t 10) thay vì oversubscribe lên 20 threads.

```
before:  86.2 tok/s (-t 20)
after:   119.8 tok/s (-t 10)
speedup: 1.39×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

Giai đoạn decode của mô hình ngôn ngữ bị nghẽn bởi băng thông bộ nhớ (Memory Bandwidth bound) chứ không phải compute bound. Trên Apple M1 Pro (10 physical cores gồm 8 Performance cores và 2 Efficiency cores), một số lượng luồng vừa phải (5-10 threads) trên kiến trúc Unified Memory đã bão hòa hoàn toàn khả năng đọc trọng số mô hình từ RAM.

Khi tăng số threads lên 20 (vượt quá 2x số core vật lý), hệ thống rơi vào trạng thái Thread Oversubscription nghiêm trọng: chi phí context switching của OS tăng vọt, L2 cache bị thrashing liên tục và các luồng tranh chấp khóa (lock contention). Đặc biệt, kiến trúc big.LITTLE khiến các luồng rơi vào 2 nhân E-core bị chậm hơn, kéo lùi toàn bộ rào chắn đồng bộ (barrier synchronization). Hạ về đúng 10 threads loại bỏ hoàn toàn các overhead này, mang lại mức tăng tốc 1.39x (từ 86.2 lên 119.8 tok/s).

---

## 6. Bonus  *(optional — tối đa 20 điểm)*

> Bỏ trống nếu không làm. Xem `bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** B2 sweep-ctx (Context length sweep đo chi phí prefill và scaling TTFT)

**Numbers:**

```
before:  115.0 ms (TTFT contribution tại 256 tokens)
after:   9675.4 ms (TTFT contribution tại 16384 tokens)
speedup: 1.31× vs linear scaling (prefill drop từ 2226.6 xuống 1693.4 tok/s)
```

**Điều này nói lên gì mà deck chưa nói:**

Chi phí prefill tăng phi tuyến tính theo độ dài context do độ phức tạp O(N^2) của Attention và áp lực phình to của KV cache trong RAM. Trong các ứng dụng RAG thực tế, việc nhồi nhét quá nhiều document chunk vào context window sẽ khiến TTFT phình to tới gần 10 giây trước khi người dùng nhận được token đầu tiên.

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

Điều ngạc nhiên nhất là việc tăng số thread CPU lên gấp đôi (-t 20) lại làm tụt tốc độ decode tới gần 30% do tranh chấp cache và scheduling overhead, chứng minh rằng trong LLM inference, hiểu rõ kiến trúc phần cứng và memory bandwidth quan trọng hơn việc tăng số luồng một cách mù quáng.

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [x] Repo GitHub ở chế độ **public**
- [x] Đã paste public URL vào VinUni LMS
- [x] **Không** commit `models/*.gguf` hay `runtime/` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.
