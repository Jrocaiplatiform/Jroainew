import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import EventSource from "react-native-sse";

const API = process.env.EXPO_PUBLIC_API_BASE_URL || "https://jrocai.online/api/v1";

type Build = {
  buildId: string;
  status: string;
  assignedBrain?: string;
};

type Screen = "home" | "build" | "activity" | "settings";

async function api(path: string, options: RequestInit = {}) {
  const token = await AsyncStorage.getItem("jroc_access_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
  const text = await response.text();
  let data: any = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { message: text }; }
  if (!response.ok) throw new Error(data?.error?.message || data?.message || `Request failed: ${response.status}`);
  return data;
}

export default function App() {
  const [screen, setScreen] = useState<Screen>("home");
  const [loggedIn, setLoggedIn] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [goal, setGoal] = useState("");
  const [build, setBuild] = useState<Build | null>(null);
  const [events, setEvents] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    AsyncStorage.getItem("jroc_access_token").then(token => setLoggedIn(!!token));
  }, []);

  const title = useMemo(() => ({
    home: "COMMAND CENTER",
    build: "UNIVERSAL BUILDER",
    activity: "LIVE ACTIVITY",
    settings: "SETTINGS",
  }[screen]), [screen]);

  async function login() {
    setBusy(true); setError("");
    try {
      const result = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      await AsyncStorage.setItem("jroc_access_token", result.accessToken);
      if (result.refreshToken) await AsyncStorage.setItem("jroc_refresh_token", result.refreshToken);
      setLoggedIn(true);
    } catch (e: any) {
      setError(e.message);
    } finally { setBusy(false); }
  }

  async function createBuild() {
    if (!goal.trim()) return;
    setBusy(true); setError(""); setEvents([]);
    try {
      const result = await api("/builder/create", {
        method: "POST",
        body: JSON.stringify({ goal, outputType: "application", priority: "high" }),
      });
      setBuild(result);
      setScreen("activity");
      if (result.buildId) streamBuild(result.buildId);
    } catch (e: any) {
      setError(e.message);
    } finally { setBusy(false); }
  }

  function streamBuild(buildId: string) {
    const tokenPromise = AsyncStorage.getItem("jroc_access_token");
    tokenPromise.then(token => {
      const source = new EventSource(`${API}/builds/${buildId}/stream`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      source.addEventListener("message", (event: any) => {
        const message = event?.data || "event";
        setEvents(prev => [message, ...prev].slice(0, 100));
      });
      source.addEventListener("error", () => {
        setEvents(prev => ["SSE connection closed or unavailable.", ...prev]);
        source.close();
      });
    });
  }

  async function logout() {
    await AsyncStorage.multiRemove(["jroc_access_token", "jroc_refresh_token"]);
    setLoggedIn(false); setBuild(null); setEvents([]);
  }

  if (!loggedIn) {
    return (
      <SafeAreaView style={styles.root}>
        <StatusBar barStyle="light-content" />
        <View style={styles.login}>
          <Text style={styles.brand}>J-ROC</Text>
          <Text style={styles.subtitle}>ACTUAL AI UNIVERSE™</Text>
          <TextInput style={styles.input} placeholder="Email" placeholderTextColor="#657080" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
          <TextInput style={styles.input} placeholder="Password" placeholderTextColor="#657080" value={password} onChangeText={setPassword} secureTextEntry />
          {error ? <Text style={styles.error}>{error}</Text> : null}
          <TouchableOpacity style={styles.primary} onPress={login} disabled={busy}>
            {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryText}>ENTER UNIVERSE</Text>}
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.root}>
      <StatusBar barStyle="light-content" />
      <View style={styles.header}>
        <View>
          <Text style={styles.brandSmall}>J-ROC AI</Text>
          <Text style={styles.title}>{title}</Text>
        </View>
        <View style={styles.live}><View style={styles.dot} /><Text style={styles.liveText}>LIVE</Text></View>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {screen === "home" && (
          <>
            <Text style={styles.hero}>What would you like to build today?</Text>
            <TouchableOpacity style={styles.card} onPress={() => setScreen("build")}>
              <Text style={styles.cardTitle}>UNIVERSAL BUILDER</Text>
              <Text style={styles.cardText}>Turn a goal into a live build using J-Roc AI, the Command Brain, workforce, swarm execution and real telemetry.</Text>
            </TouchableOpacity>
            <View style={styles.row}>
              <View style={styles.stat}><Text style={styles.statValue}>{build ? "1" : "0"}</Text><Text style={styles.statLabel}>ACTIVE BUILDS</Text></View>
              <View style={styles.stat}><Text style={styles.statValue}>{events.length}</Text><Text style={styles.statLabel}>LIVE EVENTS</Text></View>
            </View>
          </>
        )}

        {screen === "build" && (
          <>
            <Text style={styles.hero}>Describe the system you want J-ROC to build.</Text>
            <TextInput style={styles.goal} multiline placeholder="Example: Build a CRM for my music business..." placeholderTextColor="#657080" value={goal} onChangeText={setGoal} />
            {error ? <Text style={styles.error}>{error}</Text> : null}
            <TouchableOpacity style={styles.primary} onPress={createBuild} disabled={busy || !goal.trim()}>
              {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.primaryText}>START BUILD</Text>}
            </TouchableOpacity>
          </>
        )}

        {screen === "activity" && (
          <>
            <View style={styles.card}>
              <Text style={styles.cardTitle}>BUILD STATUS</Text>
              <Text style={styles.status}>{build?.status || "STREAMING"}</Text>
              {build?.assignedBrain ? <Text style={styles.cardText}>Brain: {build.assignedBrain}</Text> : null}
            </View>
            <Text style={styles.section}>REAL-TIME SSE STREAM</Text>
            {events.length === 0 ? <Text style={styles.muted}>Waiting for build events...</Text> :
              events.map((event, i) => <View key={i} style={styles.event}><Text style={styles.eventText}>{event}</Text></View>)}
          </>
        )}

        {screen === "settings" && (
          <>
            <View style={styles.card}><Text style={styles.cardTitle}>API</Text><Text style={styles.cardText}>{API}</Text></View>
            <TouchableOpacity style={styles.secondary} onPress={logout}><Text style={styles.secondaryText}>SIGN OUT</Text></TouchableOpacity>
          </>
        )}
      </ScrollView>

      <View style={styles.nav}>
        {(["home","build","activity","settings"] as Screen[]).map(item => (
          <TouchableOpacity key={item} style={styles.navItem} onPress={() => setScreen(item)}>
            <Text style={[styles.navText, screen === item && styles.navActive]}>{item.toUpperCase()}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#05070d" },
  login: { flex: 1, justifyContent: "center", padding: 28, maxWidth: 620, width: "100%", alignSelf: "center" },
  brand: { color: "#fff", fontSize: 48, fontWeight: "900", letterSpacing: 5 },
  brandSmall: { color: "#fff", fontSize: 20, fontWeight: "900", letterSpacing: 3 },
  subtitle: { color: "#8b96a8", letterSpacing: 3, marginBottom: 36 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 20, borderBottomWidth: 1, borderBottomColor: "#1b2230" },
  title: { color: "#7e8ba0", fontSize: 11, letterSpacing: 2, marginTop: 3 },
  live: { flexDirection: "row", alignItems: "center", gap: 6 },
  dot: { width: 7, height: 7, borderRadius: 7, backgroundColor: "#39e58c" },
  liveText: { color: "#39e58c", fontSize: 10, fontWeight: "800" },
  content: { padding: 20, paddingBottom: 110, maxWidth: 900, width: "100%", alignSelf: "center" },
  hero: { color: "#fff", fontSize: 30, fontWeight: "800", marginVertical: 24 },
  input: { backgroundColor: "#0d121c", borderWidth: 1, borderColor: "#202a39", color: "#fff", borderRadius: 12, padding: 15, marginBottom: 12 },
  goal: { minHeight: 180, textAlignVertical: "top", backgroundColor: "#0d121c", borderWidth: 1, borderColor: "#202a39", color: "#fff", borderRadius: 14, padding: 18, fontSize: 17, marginBottom: 16 },
  primary: { backgroundColor: "#315cff", padding: 16, borderRadius: 12, alignItems: "center", marginTop: 8 },
  primaryText: { color: "#fff", fontWeight: "900", letterSpacing: 1 },
  secondary: { borderWidth: 1, borderColor: "#293346", padding: 16, borderRadius: 12, alignItems: "center", marginTop: 12 },
  secondaryText: { color: "#c8d0dc", fontWeight: "800" },
  card: { backgroundColor: "#0c111a", borderWidth: 1, borderColor: "#1d2737", borderRadius: 16, padding: 20, marginBottom: 16 },
  cardTitle: { color: "#fff", fontWeight: "900", letterSpacing: 1, marginBottom: 10 },
  cardText: { color: "#8f9aac", lineHeight: 22 },
  row: { flexDirection: "row", gap: 12 },
  stat: { flex: 1, backgroundColor: "#0c111a", borderWidth: 1, borderColor: "#1d2737", borderRadius: 16, padding: 20 },
  statValue: { color: "#fff", fontSize: 28, fontWeight: "900" },
  statLabel: { color: "#718097", fontSize: 9, letterSpacing: 1, marginTop: 4 },
  status: { color: "#39e58c", fontSize: 22, fontWeight: "900", marginBottom: 6 },
  section: { color: "#718097", fontSize: 11, letterSpacing: 2, marginVertical: 14 },
  event: { backgroundColor: "#080c13", borderLeftWidth: 2, borderLeftColor: "#315cff", padding: 12, marginBottom: 7, borderRadius: 5 },
  eventText: { color: "#b8c2d1", fontFamily: "monospace", fontSize: 12 },
  muted: { color: "#657080" },
  error: { color: "#ff6b7a", marginBottom: 12 },
  nav: { position: "absolute", bottom: 0, left: 0, right: 0, flexDirection: "row", backgroundColor: "#090d15", borderTopWidth: 1, borderTopColor: "#1b2230", paddingVertical: 10, paddingHorizontal: 4 },
  navItem: { flex: 1, alignItems: "center", padding: 10 },
  navText: { color: "#596578", fontSize: 9, fontWeight: "800" },
  navActive: { color: "#fff" }
});
