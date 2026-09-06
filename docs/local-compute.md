# Dual compute (phone / SBC + local weights)

Phone is the field UI. SBC holds Ollama and the weights. That is the Asimov 1 pattern applied to a kit, not a humanoid.

## Hub

```bash
export OLLAMA_HOST=http://<jarvis>:11434
export OLLAMA_MODEL=<smoke-model>
python -m isurvive serve
```

`GET /api/hub` reports whether Ollama answered `/api/tags`.

If Ollama is down, `POST /api/operator` still returns the deterministic briefing from `operator/knowledge`. Check **Rewrite with local Ollama** only when the smoke model is live.

## Hardware (ISV-CM-01 / ISV-PM-01)

- Pi-class SBC + 128 GB storage in the printed tray
- Phone over USB-C
- 65 W PD bank and 40 W fold solar

Keep medical and personal notes off the disk you might commit. Comfy stays on the desk (Jarvis) until that install is finished; the field kit does not depend on it.
