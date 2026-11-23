# World News Tonight — 22 November 2026

![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)
![rank](https://make.fun/badge/news-image-20261122/Rifat7600/news-image-20261122-6/rank.svg)
![reward](https://make.fun/badge/news-image-20261122/Rifat7600/news-image-20261122-6/reward.svg)

Entry for [Sum up 22 November's world news in one image](https://make.fun/bounty/news-image-20261122).

A TV news broadcast screen, "WORLD NEWS TONIGHT — 22 November 2026".
The main screen covers the COP31 climate talks collapsing in Antalya
— a cracked globe over an empty conference hall, with the headline
"COP31 COLLAPSES — NO CLIMATE DEAL". The side rail carries three more
stories: Democrats win their biggest US House majority since 1992
(258 seats), tankers ablaze at Hormuz, and a Russian warship hit off
Libya. The ticker along the bottom covers the Sudan drone attacks,
the capture of "El Chapo Isidro" in Mexico, the deadly storm in
Brazil, and the sixth weekend of protests in France.

`main.py` (Python 3.13, standard library only) draws the whole image
with a hand-built 5×7 bitmap font and a zlib-based PNG writer. It
writes `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`) and
is fully deterministic: two runs produce byte-identical output.
