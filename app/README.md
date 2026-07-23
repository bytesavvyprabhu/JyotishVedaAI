# JyotishVedaAI — Mobile App

A Flutter app for the JyotishVedaAI backend: enter your birth details and a
question, get your Vedic chart + an AI-generated reading.

## Screens

- `lib/screens/birth_form_screen.dart` — name, place/date/time of birth, question
- `lib/screens/result_screen.dart` — ascendant/moon sign, current mahadasha,
  planetary positions, and the AI answer
- `lib/services/api_service.dart` — talks to the FastAPI `/consult` endpoint
- `lib/models/consult_result.dart` — response models

## Running the backend so your phone can reach it

By default FastAPI/uvicorn only listens on `127.0.0.1`, which a phone can't
reach. From the `JyotishVedaAI` project root, start it bound to all
interfaces instead:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then find your computer's LAN IP (phone and computer must be on the same
Wi-Fi):

```powershell
ipconfig   # look for IPv4 Address, e.g. 192.168.1.42
```

## Running the app

The API base URL defaults to `http://10.0.2.2:8000`, which only works for the
**Android emulator** (it's a special alias for the host machine's localhost).

- **Android emulator**: no change needed, just `flutter run`.
- **iOS simulator**: `flutter run --dart-define=API_BASE_URL=http://localhost:8000`
- **Physical phone (Android or iOS) over Wi-Fi**:
  ```bash
  flutter run --dart-define=API_BASE_URL=http://<your-computer-LAN-IP>:8000
  ```

`android/app/src/main/AndroidManifest.xml` already has the `INTERNET`
permission and `usesCleartextTraffic="true"` enabled so plain `http://` works
during development. For a production release, put the backend behind HTTPS
and remove `usesCleartextTraffic`.
