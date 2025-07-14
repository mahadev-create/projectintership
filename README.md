## 🔐 API Keys and External Services Used

This project, **MythoPersona-AI**, uses the following APIs to enrich its features:

---

### 1. OpenRouter API (LLM for Story Generation)
- **Purpose**: Generates a 7-part mythological origin story based on user's astrology and persona profile.
- **Model Used**: `mistralai/mistral-small-3.2-24b-instruct:free`
- **Provider**: [OpenRouter.ai](https://openrouter.ai)
- **How to Get API Key**:
  - Sign up at [https://openrouter.ai](https://openrouter.ai)
  - Navigate to your dashboard → Get Free API Key.
  - Add it to a `.env` file like this:

    ```
    OPENROUTER_API_KEY=your-api-key-here
    ```

---

### 2. AstroSeek Horoscope API (Astrology Profile Extraction)
- **Purpose**: Extracts zodiac sign, moon sign, nakshatra, and other astrological traits based on birth details.
- **Provider**: [AstroSeek](https://horoscopes.astro-seek.com/)
- **API Endpoint**: Internal endpoint in the project, powered by horo_module/horo_extractor.py
- **No key required**, but internet access is needed.


```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
