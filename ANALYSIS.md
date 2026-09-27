# Reference Video Analysis — Kinetic Typography Reel

Source file: `screen-20260828-071450-1787881461288.mp4~2 (1).mp4`
Analyzed: 2026-09-27 (frame-by-frame sequential decode, 781 frames)

## 1. File specs
- Container: MP4 (H.264 video + AAC audio, 44.1 kHz)
- Resolution: 1030×586 (landscape ~16:9) — a screen capture of an Instagram reel being watched
- Frame rate: ~30.3 fps, Duration: ~26 s (ends abruptly mid-word; starts mid-fade)
- On-screen IG rail throughout: ~43.9K likes, 298 comments (right edge)

## 2. Concept (one line)
Hinglish "make money online" listicle reel: hook → website #1 (Luel.ai) → website #2
(Promote.fun) → follow CTA, alternating kinetic-typography cards with phone screen
recordings, dressed with meme stickers and a signature walking-cat watermark.

## 3. Timeline & transcript (ground truth from sequential decode)
| Time | Visual | Text / content |
|---|---|---|
| 0.00–0.75 | Maroon card, white bold sans fades in | "bhai" |
| 0.75–1.50 | Yellow words slide in; kitten rises from bottom | "bhai **kuch kamane**" |
| 1.50–2.75 | "ke liye" above; line types in letter-by-letter below; kitten dances bottom-left | "ke liye / bhai **kuch kamane** / ye do website batata hun" |
| 3.00–4.25 | Yellow line; Spider-Man drops from top; white serif slides in | "**bina kisi comment wali** / bakwaas ke" (= no "comment for link" bait) |
| 4.50–5.81 | Kinetic assembly: vertical "PEHLI" + yellow "website" + "ka/naam" + vertical "hai" | "PEHLI website ka naam hai" |
| 5.81 CUT | Google search result | "Luel - AI / https://www.luel.ai / Two-sided marketplace for on-demand video and audio training data…" |
| 6.90 CUT | luel.ai homepage | Hero, "Browse Catalog", "Talk with our team", "What's inside every delivery" |
| 7.72 CUT | Scrolling luel.ai | Logos (Cambridge, CMU, ETH Zürich), "Premium collections, ready to license", Speech/Sensor/Video categories, dataset search bar |
| 11.52 CUT | Maroon card, yellow + Naruto drops from top, serif types in | "**2. website** / ka naam hai" |
| ~12.95–13.83 | White diagonal wipe → Google search "promote fun" | promote.fun result: "Turn your content distribution into revenue…" |
| 13.83 CUT | Maroon card, white serif staggered letter animation | "yaha per kaafi saare" (sentence completed visually by next shot) |
| 15.08 CUT | promote.fun screen recording: Active campaigns | CALLE 24 ($1,500 / $0.50), DEXTER AND THE MOONROCKS ($4,000) |
| ~16.50 | "Complete" campaigns | JACKASS ($2,800 / $1.75), BIA ($2,500) |
| ~18.50–21.50 | Jackass Trailer campaign page (red circle annotation), scroll | Budget $2,800 paid, $1.75/1k views, Instagram, Total Views 2.2M, 85 submissions, launch Apr 28 2026 |
| ~21.50–24.49 | Scroll to Campaign Statistics + Overview | Bar chart "Today 2.2M", Approved/Pending/Denied |
| 24.49 CUT | Maroon outro card, italic serif + yellow bold italic | "and don't forget / **to press** / fo…" (recording ends mid-word, almost certainly "follow") |

Persistent: black-cat silhouette walking along the bottom (creator watermark); IG action
rail on right; phone status bar (11:32→11:33) during browser segments.

## 4. Design system
- Background: deep maroon `#5B2036` (typo cards)
- Accent/keyword: warm yellow `#F5C510` (money/action words: kuch kamane, website, 2. website, to press)
- Text: off-white `#FDF5FA`
- Type pairing: heavy rounded sans (Hinglish hook words) + elegant italic serif
  (connectors and English lines: "bakwaas ke", "ka naam hai", "yaha per kaafi saare",
  "and don't forget")
- Layout: centered, dense, overlapping; vertical rotated words as graphic devices
  ("PEHLI", "hai"); sticker + headline composites (kitten, Spider-Man hanging from top
  edge, Naruto laughing above headline)

## 5. Motion & editing grammar
- Word-by-word slide/fade entrances synced to voiceover (~0.25–0.5 s per beat)
- Letter-by-letter typewriter reveals for punchlines ("ye do website batata hun",
  "yaha per kaafi saare", "ka naam hai")
- Stickers drop/rise from frame edges; kitten bobs like a dance loop
- Hard cuts between sections (5.81 / 11.52 / 13.83 / 15.08 / 24.49); jump cuts inside
  screen recordings (6.90, 7.72); one white diagonal wipe (site #2 reveal)
- Proof pattern per website: Google search (name reveal + legitimacy) → homepage →
  scroll to money/category proof → stats. Red hand-drawn circle highlights key item.
- Incomplete-sentence hook: "yaha per kaafi saare…" resolves visually, forcing watch-through.

## 6. Retention devices
Cold-open money hook in first second → anti-bait trust line ("bina kisi comment wali
bakwaas") → numbered list → meme stickers every ~3 s → dollar-amount proof
screenshots → follow CTA. No dead frames; text or scroll motion in every shot.

## 7. Audio (not transcribed)
AAC 44.1 kHz stereo track present — almost certainly Hindi voiceover + trending
background audio, with text beats timed to the VO. Transcription needs a STT pass.

## 8. Recreation blueprint
1. 9:16 (1080×1920) comps; maroon `#5B2036` base; same two-font pairing.
2. Build one kinetic-type template: word-level position/opacity keyframes + typewriter preset.
3. Structure: hook card (0–3 s) → trust line (3–5 s) → "N. website ka naam hai" card →
   screen recording (search → home → proof scroll, 2 jump cuts) → bridge serif line →
   repeat → "and don't forget to press follow" outro.
4. Overlay signature watermark (walking cat) + meme sticker per card + IG-safe margins.
5. Beat-map text entrances to VO waveform; hard cuts on section changes, one wipe for reveals.
