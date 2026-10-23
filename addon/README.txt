Vocalizer Mobile TTS 0.1.1 for NVDA

Install vocalizerMobileTTS-0.1.1.nvda-addon, restart NVDA, and select Vocalizer Mobile TTS in the synthesizer dialog. The voice list contains English (United States) and Spanish (Mexico). This driver has a separate identity from Voice Signal TTS and the earlier Motorola add-ons.

Settings: voice, rate, pitch, volume. Rate 50 is the original speed; 0 is half speed and 100 is double speed. Pitch 50 is the original pitch; the extremes shift approximately six semitones down/up while preserving tempo. Volume uses nvwave. Playback uses NVDA's selected output device. Language changes, spelling, pauses, index notifications, cancellation and long-text chunking are supported.

Original ARM firmware synthesis runs in an isolated bundled Python/Unicorn worker. Models are included for both languages. No phone, installation of Python, network access, or model download is needed.

Latency: redundant per-audio-frame timeout monitors were removed, while a process watchdog remains. Default pitch streams PCM directly to nvwave. Non-default pitch uses FFmpeg on short text chunks and therefore has additional latency. Each text chunk runs in a fresh process to bound the original engine's allocations and make cancellation reliable. This version does not claim an optimized persistent engine.

Validation used actual bundled processes with an NVDA playback adapter, not a live NVDA session. Both voices and rate extremes were synthesized; pitch samples, output-device selection, volume, pause/resume, cancellation/recovery, indices, language switching, long input and termination were tested. The original build was also tested successfully by its user in NVDA.

Source firmware: VRZ_V860_00.21.13P_PRItt23853_CUSTOMER_UPGRADE_01.shx.gz. Embedded Nuance/VoiceSignal ELVIS model assets remain original proprietary firmware content.  Included Python, Unicorn and FFmpeg retain their supplied licensing files.

Updating: install this package over the earlier phone-named add-on. Internal identifiers are retained for settings compatibility.

Source builds: the repository contains adapter source. Copy the engine runtime, dependencies and firmware assets from the corresponding release package into addon/engine before running build.py. Those assets are excluded from Git history.
