# Multilingual support

AI Cinema Studio separates three language choices:

1. **Interface language** — English, French, or Arabic. Arabic switches the Qt UI to right-to-left layout.
2. **Project output language** — auto-detect from the creative brief, a listed language, or a custom language name. This applies to dialogue, narration, lyrics, on-screen wording, and human-readable project metadata.
3. **Visual prompt language** — English by default for broad compatibility with image/video generators, or the project output language.

The language policy is passed to Director, Scriptwriter, Visual, Audio Planning, and Assembler. Schema keys and technical enum values are never translated. Dialogue and narration are preserved as Unicode text through downstream audio planning.

## Important limitations

UTF-8 is an encoding standard. It preserves characters; it does not make a language model understand every language. Model performance varies by language, dialect, writing system, and task. Rare languages and regional dialects should be validated with representative test prompts. TTS and media providers may have narrower language/voice support than text models.

## File encoding

Translation catalogs and all application-owned text outputs are UTF-8. JSON is serialized with `ensure_ascii=False`. API keys remain in the operating-system credential vault when available, or in memory for the current session if no secure backend is available.
