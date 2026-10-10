# Motor de crescimento orgânico

Ferramentas para crescer no Instagram, TikTok, YouTube e LinkedIn sem depender de anúncio.
O raciocínio por trás de cada uma está em [`../ESTRATEGIA.md`](../ESTRATEGIA.md).

```bash
pip install -r crescimento/requirements.txt

# 1. Diagnóstico sobre os dados exportados do Metricool (crescimento/dados/*.csv)
python -m crescimento.diagnostico

# 2. Grade da semana (1 ideia -> 4 redes, horários do Metricool). --json para a rotina
python -m crescimento.calendario 2026-10-12

# 3. Ganchos e legendas por rede com o Claude (precisa de ANTHROPIC_API_KEY)
python -m crescimento.ganchos "Ideia: 13º salário já gasto antes de cair" "Educação Financeira"

# 4. Cortes verticais de um vídeo longo (live, entrevista, episódio do Dr. Di)
python -m crescimento.cortes episodio.mp4 episodio.srt

python -m pytest -q crescimento/tests
```

| Arquivo | O que faz |
|---|---|
| `diagnostico.py` | taxa de 3 segundos x views, quem gera envio, desempenho por horário, pilar e duração |
| `calendario.py` | grade semanal com Trial Reels às terças e quintas e horários escalonados por rede |
| `ganchos.py` | pacote por rede com limites de caractere checados (`len`), com a voz e as regras de texto do autor |
| `cortes.py` | acha frases com cara de gancho no .srt e gera os comandos ffmpeg 9:16 |
| `rotina_diaria.md` | prompt da Routine diária (Metricool + Todoist + Gmail), que só deixa rascunhos |
| `dados/` | snapshot do Metricool em 10/10/2026 (TikTok: amostra de 49 vídeos) |
