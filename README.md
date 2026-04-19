# Meteo Agent WhatsApp (Python)

Questo progetto contiene uno script Python (`meteo_agent.py`) che:

1. Recupera il meteo di oggi per la tua città da OpenWeatherMap
2. Crea un messaggio di buongiorno con i dati meteo
3. Invia il messaggio via WhatsApp usando Twilio

## 1) Prerequisiti

- Account GitHub
- Account OpenWeatherMap
- Account Twilio

## 2) Ottenere la chiave API OpenWeatherMap

1. Vai su https://openweathermap.org/ e crea un account.
2. Conferma l'email e accedi.
3. Apri la sezione **API keys** nel tuo profilo.
4. Crea una nuova key (oppure usa quella di default).
5. Copia la key: la userai come secret GitHub `OPENWEATHER_API_KEY`.

> Nota: una nuova key può impiegare qualche minuto prima di diventare attiva.

## 3) Ottenere credenziali Twilio + WhatsApp Sandbox

1. Vai su https://www.twilio.com/ e crea un account.
2. Dalla Console copia:
   - `Account SID` → secret `TWILIO_ACCOUNT_SID`
   - `Auth Token` → secret `TWILIO_AUTH_TOKEN`
3. Apri **Messaging > Try it out > Send a WhatsApp message**.
4. Attiva la sandbox WhatsApp.
5. Prendi il numero mittente sandbox (es. `whatsapp:+14155238886`) → secret `TWILIO_WHATSAPP_FROM`.
6. Collega il tuo numero personale alla sandbox inviando il codice di join indicato da Twilio.
7. Il destinatario sarà il tuo numero in formato WhatsApp E.164 (es. `whatsapp:+393331234567`) → secret `TWILIO_WHATSAPP_TO`.

## 4) Configurare i Secrets e Variables su GitHub

Nel repository GitHub vai in **Settings > Secrets and variables > Actions**.

### Secrets da creare

- `OPENWEATHER_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`
- `TWILIO_WHATSAPP_TO`

### Variables da creare

- `CITY_NAME` (es. `Milano`)
- `COUNTRY_CODE` (opzionale, es. `IT`)

## 5) Esecuzione automatica con GitHub Actions

Il workflow `.github/workflows/meteo_agent.yml` esegue lo script:

- Ogni giorno alle **08:00 UTC** (`0 8 * * *`)
- Manualmente con **Run workflow** (evento `workflow_dispatch`)

Se vuoi le 08:00 italiane, modifica il cron in base a ora legale/solare.

## 6) Test locale (opzionale)

```bash
python -m venv .venv
source .venv/bin/activate
pip install requests twilio

export OPENWEATHER_API_KEY="..."
export TWILIO_ACCOUNT_SID="..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"
export TWILIO_WHATSAPP_TO="whatsapp:+39..."
export CITY_NAME="Milano"
export COUNTRY_CODE="IT"

python meteo_agent.py
```

## 7) File principali

- `meteo_agent.py`: logica dell'agente
- `.github/workflows/meteo_agent.yml`: schedulazione automatica su GitHub Actions
