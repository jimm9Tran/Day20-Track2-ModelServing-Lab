# Bonus - Context-length sweep (prefill cost)

Host `Darwin-arm64` · llama.cpp `b10488` ·
`threads=10` `ngl=99` · RAM 32.0 GB

| Prompt tokens | Prefill (tok/s) | TTFT contribution (ms) | vs linear scaling |
|:--|--:|--:|--:|
| 256 | 2226.6 | 115.0 | 1.00x |
| 1024 | 2296.8 | 445.8 | 0.97x |
| 2048 | 2224.6 | 920.6 | 1.00x |
| 4096 | 2150.4 | 1904.8 | 1.04x |
| 8192 | 1977.4 | 4142.7 | 1.13x |
| 16384 | 1693.4 | 9675.4 | 1.31x |

At 16384 tokens, prefill costs **9675 ms** --
1.31x what linear scaling from the smallest point would predict. That excess
is attention's O(N^2) term becoming visible, and every millisecond of it lands in TTFT
before the user sees a single token.

Either way, this is the number to remember when someone proposes stuffing more retrieved
context into a RAG prompt "because the context window allows it". Prefill is paid in full,
on every request, before the first token appears.

## Your finding

Từ 256 đến 2048 tokens, tốc độ prefill duy trì ổn định ở mức ~2225-2296 tok/s (tăng tuyến tính với thời gian prefill dưới 1 giây). Tuy nhiên, khi context vượt quá 4096 tokens, tốc độ prefill bắt đầu giảm rõ rệt (từ 2224 xuống 1693 tok/s tại 16k tokens) và thời gian prefill tăng vọt lên **9.68 giây** (gấp 1.31x mức tăng tuyến tính).

Khúc uốn phi tuyến tính này phản ánh chi phí $O(N^2)$ của cơ chế self-attention và áp lực băng thông khi ma trận KV cache phình to trong Unified Memory. Điều này cho thấy trong hệ thống RAG, không nên nhồi nhét quá nhiều chunk ngữ cảnh vào prompt (nên giới hạn dưới 2000 tokens) để giữ TTFT dưới 1s, tránh biến giai đoạn prefill thành điểm nghẽn chính của hệ thống.

