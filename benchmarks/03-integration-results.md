# 03 - Integrate: RAG pipeline run

Host `Darwin-arm64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 838.0 | 838.1 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 892.7 | 892.7 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 993.4 | 993.4 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **908.0** · total **908.1**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the provided context, **Goodput** is more useful than raw throughput because it filters out requests that do not meet specific targets (TTFT and TPOT) and only counts those that do.

Raw throughput ignores SLOs (specifically throughput at saturation), whereas Goodput counts only the requests per second that met the targets.

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation in GPU memory** caused by storing the Key-Value (KV) cache in non-contiguous pages.

By organizing the KV cache into non-contiguous pages, the architecture eliminates the wasted space that would otherwise exist if all KV data were packed into a single contiguous block. This optimization allows the engine to utilize more of the available

**When does splitting prefill and decode help?**

> The context explicitly states that splitting prefill and decode helps when **prefill is compute-bound and decode is memory-bandwidth-bound**.

This suggests that the system uses a strategy where the prefill phase (which is computationally expensive) is split into multiple smaller chunks, while the decode phase (which is memory-bound) is split into multiple smaller chunks. This allows the engine to


## Which N16-N19 pieces are real

| Module | Component | Trạng thái |
|:---|:---|:---|
| N16 | Cloud / IaC | **Stub** (chạy trên localhost) |
| N17 | Data pipelines | **Stub** (in-memory list) |
| N18 | Lakehouse | **Stub** (dict `TOY_DOCS`) |
| N19 | Vector & Features | **Stub** (keyword overlap retrieval) |
| N20 | Serving Stack | **Real** (`llama-server` b10488 HTTP OpenAI API) |

Khâu LLM chiếm tới **100%** tổng thời gian xử lý (trung bình 908.0 ms / 908.1 ms total), hoàn toàn khớp với kỳ vọng vì retrieval chỉ là in-memory search trên tập toy docs cực nhỏ. 

Nếu phải giảm độ trễ pipeline đi 2x, tôi sẽ tấn công trực tiếp vào **khâu LLM**:
1. Áp dụng **Prompt Caching / Prefix Caching** để tái sử dụng KV cache của system prompt và context chung, triệt tiêu thời gian prefill.
2. Tối ưu prompt để giới hạn số output token ngắn gọn hơn hoặc áp dụng **Speculative Decoding** với draft model siêu nhỏ để tăng tốc độ decode.

