# J-ROC AI Universe — Native Mobile + Tablet App

This directory is the native React Native/Expo client for J-ROC AI Universe.

It is a real native application target for Android, iPhone, and tablets. It connects to the existing J-ROC backend rather than replacing the backend.

## Local development

From `mobile/`:

```bash
npm install
npx expo start
```

Android:

```npx expo run:android```

iOS requires macOS/Xcode for local compilation:

```npx expo run:ios```

For cloud iOS builds from Windows/Linux, use EAS Build.

## Installable Android build

Preview APK:

```bash
npx eas build --platform android --profile preview
```

Production Android:

```bash
npx eas build --platform android --profile production
```

## iOS build

```bash
npx eas build --platform ios --profile production
```

EAS can build Android and iOS from the same React Native project and can provide internal distribution builds before store release.

## Backend

Set:

```text
EXPO_PUBLIC_API_BASE_URL=https://jrocai.online/api/v1
```

The app uses the existing J-ROC authentication, Universal Builder, and build-event streaming APIs.

## Current native surfaces

- J-ROC authentication
- Universal Builder
- Live build status
- SSE build stream
- Command Center
- Activity stream
- Settings/sign-out
- Responsive phone/tablet layout
