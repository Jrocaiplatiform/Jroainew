import React, { useState } from "react";
import { ActivityIndicator, SafeAreaView, StatusBar, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { WebView } from "react-native-webview";

const APP_URL = "https://jrocai.online";

export default function App() {
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <SafeAreaView style={styles.root}>
        <StatusBar barStyle="light-content" />
        <View style={styles.center}>
          <Text style={styles.brand}>J-ROC AI</Text>
          <Text style={styles.message}>Unable to connect to J-ROC AI Universe.</Text>
          <TouchableOpacity style={styles.button} onPress={() => setFailed(false)}>
            <Text style={styles.buttonText}>RECONNECT</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar barStyle="light-content" backgroundColor="#05070d" />
      {loading && (
        <View style={styles.loading}>
          <ActivityIndicator size="large" color="#315cff" />
          <Text style={styles.loadingText}>CONNECTING TO J-ROC AI UNIVERSE</Text>
        </View>
      )}
      <WebView
        source={{ uri: APP_URL }}
        style={styles.webview}
        onLoadStart={() => { setLoading(true); setFailed(false); }}
        onLoadEnd={() => setLoading(false)}
        onError={() => { setLoading(false); setFailed(true); }}
        javaScriptEnabled
        domStorageEnabled
        sharedCookiesEnabled
        thirdPartyCookiesEnabled
        allowsBackForwardNavigationGestures
        setSupportMultipleWindows={false}
        originWhitelist={["https://*"]}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#05070d" },
  webview: { flex: 1, backgroundColor: "#05070d" },
  loading: { ...StyleSheet.absoluteFillObject, zIndex: 10, alignItems: "center", justifyContent: "center", backgroundColor: "#05070d" },
  loadingText: { color: "#8b96a8", marginTop: 14, fontSize: 11, fontWeight: "800", letterSpacing: 1.5 },
  center: { flex: 1, alignItems: "center", justifyContent: "center", padding: 28, backgroundColor: "#05070d" },
  brand: { color: "#fff", fontSize: 42, fontWeight: "900", letterSpacing: 4 },
  message: { color: "#8b96a8", textAlign: "center", marginTop: 12, marginBottom: 24 },
  button: { backgroundColor: "#315cff", paddingHorizontal: 24, paddingVertical: 14, borderRadius: 10 },
  buttonText: { color: "#fff", fontWeight: "900", letterSpacing: 1 }
});
