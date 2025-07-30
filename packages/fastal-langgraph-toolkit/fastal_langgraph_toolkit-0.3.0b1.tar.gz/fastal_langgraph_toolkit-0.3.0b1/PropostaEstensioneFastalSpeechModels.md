# Proposta di Estensione del Package fastal-langgraph-toolkit per Modelli Speech

## Executive Summary

Propongo di estendere il package `fastal-langgraph-toolkit` per includere il supporto ai modelli speech-to-text (STT) e text-to-speech (TTS), mantenendo la stessa architettura elegante già presente per LLM ed embeddings.

## Analisi dell'architettura esistente

Il package attualmente implementa un pattern factory molto pulito con:

1. **Factory separate** per LLM (`LLMFactory`) ed embeddings (`EmbeddingFactory`)
2. **ModelFactory unificata** che espone entrambe le factory
3. **Sistema di provider** modulare con:
   - Classi base astratte (`BaseProvider`)
   - Protocolli ben definiti per ogni tipo di modello
   - Gestione automatica della disponibilità dei provider
4. **Lazy loading** dei modelli per ottimizzare le risorse

## Proposta di implementazione

### 1. Nuovi protocolli per modelli Speech

```python
# In src/fastal/langgraph/toolkit/models/base.py

class SpeechToTextProviderProtocol(Protocol):
    """Protocol defining the interface for speech-to-text providers."""
    
    async def transcribe(
        self, 
        audio_data: bytes, 
        mime_type: str,
        language: str | None = None,
        **kwargs
    ) -> TranscriptionResult:
        """Transcribe audio to text."""
        ...

class TextToSpeechProviderProtocol(Protocol):
    """Protocol defining the interface for text-to-speech providers."""
    
    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        language: str | None = None,
        **kwargs
    ) -> AudioResult:
        """Synthesize text to audio."""
        ...
```

### 2. Struttura delle directory

```
src/fastal/langgraph/toolkit/models/providers/
├── embeddings/
├── llm/
├── stt/  # Nuovo
│   ├── __init__.py
│   ├── openai.py      # OpenAI Whisper
│   ├── google.py      # Google Cloud Speech-to-Text
│   └── azure.py       # Azure Cognitive Services
└── tts/  # Nuovo (per futura espansione)
    ├── __init__.py
    ├── openai.py      # OpenAI TTS
    ├── google.py      # Google Cloud Text-to-Speech
    └── elevenlabs.py  # ElevenLabs
```

### 3. Factory per Speech Models

```python
# In src/fastal/langgraph/toolkit/models/factory.py

class STTFactory:
    """Factory for creating speech-to-text instances."""
    
    _provider_classes = {
        "openai": OpenAISTTProvider,
        "google": GoogleSTTProvider,
        "azure": AzureSTTProvider,
    }
    
    @classmethod
    def create_stt(
        cls,
        provider: str,
        model_name: str | None = None,
        provider_config: Any | None = None,
        **kwargs
    ) -> BaseSpeechToText:
        """Create a speech-to-text instance."""
        # Implementazione simile a LLMFactory
```

### 4. Estensione della ModelFactory unificata

```python
# In src/fastal/langgraph/toolkit/models/__init__.py

class ModelFactory:
    """Unified factory for creating AI models."""
    
    # Metodi esistenti...
    
    @classmethod
    def create_speech_to_text(cls, provider: str, model: str = None, config: dict = None, **kwargs):
        """Create a speech-to-text instance."""
        return STTFactory.create_stt(provider, model, config, **kwargs)
    
    @classmethod
    def create_text_to_speech(cls, provider: str, model: str = None, config: dict = None, **kwargs):
        """Create a text-to-speech instance."""
        return TTSFactory.create_tts(provider, model, config, **kwargs)
```

### 5. Tipi di dati comuni

```python
# In src/fastal/langgraph/toolkit/models/types.py (nuovo file)

from typing import TypedDict, List
from dataclasses import dataclass

class TranscriptionResult(TypedDict):
    text: str
    language: str
    confidence: float
    duration_seconds: float
    segments: List[TranscriptionSegment] | None
    warnings: List[str]

@dataclass
class AudioResult:
    audio_data: bytes
    mime_type: str
    duration_seconds: float
    sample_rate: int
```

### 6. Esempio di provider implementation

```python
# In src/fastal/langgraph/toolkit/models/providers/stt/openai.py

class OpenAISTTProvider(BaseProvider):
    """OpenAI Whisper speech-to-text provider."""
    
    def _create_model(self) -> OpenAISpeechToText:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("Install openai: uv add openai")
        
        client = AsyncOpenAI(api_key=self.config.api_key)
        return OpenAISpeechToText(client, self.model_name or "whisper-1")
    
    async def transcribe(self, audio_data: bytes, mime_type: str, **kwargs) -> TranscriptionResult:
        # Implementazione specifica per OpenAI Whisper
```

## Vantaggi dell'approccio

1. **Coerenza**: Stesso pattern architetturale per tutti i tipi di modelli
2. **Riusabilità**: I componenti speech saranno disponibili per tutti i progetti Fastal
3. **Estendibilità**: Facile aggiungere nuovi provider
4. **Type safety**: Uso di Protocol e TypedDict per type hints robusti
5. **Async-first**: Supporto nativo per operazioni asincrone

## Configurazione di esempio

```python
# Utilizzo nel progetto BYO-Me
from fastal.langgraph.toolkit import ModelFactory

# Configurazione provider
stt_config = {
    "api_key": os.getenv("OPENAI_API_KEY")
}

# Creazione del trascrittore
transcriber = ModelFactory.create_speech_to_text(
    provider="openai",
    model="whisper-1",
    config=stt_config
)

# Utilizzo
result = await transcriber.transcribe(
    audio_data=audio_bytes,
    mime_type="audio/mpeg"
)
```

## Gestione delle dipendenze

Aggiornamento di `pyproject.toml`:

```toml
[project.optional-dependencies]
stt = [
    "openai>=1.0.0",
    "google-cloud-speech>=2.0.0",
    "azure-cognitiveservices-speech>=1.0.0",
]
tts = [
    "openai>=1.0.0", 
    "google-cloud-texttospeech>=2.0.0",
    "elevenlabs>=0.3.0",
]
```

## Testing

1. **Unit tests** per ogni provider con mock delle API esterne
2. **Integration tests** con file audio di esempio
3. **Test di performance** per trascrizioni lunghe

## Timeline proposta

1. **Fase 1**: Implementazione STT con provider OpenAI (1-2 giorni)
2. **Fase 2**: Aggiunta provider Google e Azure (2-3 giorni)
3. **Fase 3**: Implementazione TTS base (3-4 giorni)
4. **Fase 4**: Testing e documentazione (2 giorni)

## Considerazioni aggiuntive

1. **Caching**: Possibilità di cache per trascrizioni identiche
2. **Streaming**: Supporto per trascrizione in tempo reale
3. **Batch processing**: Elaborazione efficiente di multiple richieste
4. **Rate limiting**: Gestione integrata dei limiti API

## Conclusione

Questa estensione manterrà il package fastal-langgraph-toolkit come soluzione unificata per tutti i modelli AI, aumentandone significativamente il valore per i progetti aziendali.