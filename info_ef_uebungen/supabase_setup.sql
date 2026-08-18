-- ══════════════════════════════════════════════════════════════
--  Supabase Setup – Interaktive Arbeitsblätter
--  Ausführen im Supabase SQL-Editor (Dashboard → SQL Editor)
-- ══════════════════════════════════════════════════════════════


-- ── 1. Tabelle anlegen ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS arbeitsblatt_antworten (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Verknüpfung zum eingeloggten Schüler (aus Supabase Auth)
  user_id          UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Welches Arbeitsblatt? (z.B. 'java_musikplayer_v1')
  -- Zusammen mit user_id eindeutig → ein Eintrag pro Schüler pro Blatt
  arbeitsblatt     TEXT        NOT NULL,

  -- Alle Antworten als JSON-Objekt, z.B.:
  -- { "q1": "b", "q2": "a", "q8": "Die Methode setzt spielt auf true …" }
  antworten        JSONB       NOT NULL DEFAULT '{}',

  -- Automatischer Zeitstempel beim Anlegen
  erstellt_am      TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Wird bei jedem Speichern vom Frontend gesetzt
  gespeichert_am   TIMESTAMPTZ,

  -- Eindeutig: ein Schüler hat pro Arbeitsblatt genau einen Eintrag
  CONSTRAINT unique_user_arbeitsblatt UNIQUE (user_id, arbeitsblatt)
);

-- Kommentar zur Tabelle
COMMENT ON TABLE arbeitsblatt_antworten IS
  'Speichert die Antworten von Schüler*innen zu interaktiven HTML-Arbeitsblättern.';

COMMENT ON COLUMN arbeitsblatt_antworten.antworten IS
  'JSONB-Objekt mit allen Antworten des Schülers, z.B. {"q1":"b","q8":"Freitext…"}';


-- ── 2. Row Level Security (RLS) aktivieren ──────────────────
--  Ohne RLS könnte jeder Schüler die Antworten aller anderen lesen!
ALTER TABLE arbeitsblatt_antworten ENABLE ROW LEVEL SECURITY;


-- ── 3. RLS-Policies definieren ──────────────────────────────

-- Schüler darf nur seine eigenen Zeilen lesen
CREATE POLICY "Schüler liest eigene Antworten"
ON arbeitsblatt_antworten
FOR SELECT
USING ( auth.uid() = user_id );

-- Schüler darf nur eigene Zeilen einfügen
CREATE POLICY "Schüler legt eigene Antworten an"
ON arbeitsblatt_antworten
FOR INSERT
WITH CHECK ( auth.uid() = user_id );

-- Schüler darf nur eigene Zeilen aktualisieren
CREATE POLICY "Schüler aktualisiert eigene Antworten"
ON arbeitsblatt_antworten
FOR UPDATE
USING ( auth.uid() = user_id )
WITH CHECK ( auth.uid() = user_id );


-- ── 4. Index für schnelle Abfragen ──────────────────────────
--  Optimiert die Abfrage "Zeige alle Antworten von Schüler X zu Blatt Y"
CREATE INDEX IF NOT EXISTS idx_antworten_user_blatt
ON arbeitsblatt_antworten (user_id, arbeitsblatt);


-- ══════════════════════════════════════════════════════════════
--  LEHRERANSICHT (optional)
--  Ermöglicht einem Service-Role-Account alle Einträge zu lesen,
--  z.B. für eine separate Auswertungsseite mit dem service_role key.
--  ACHTUNG: Den service_role key NIE im Frontend verwenden!
-- ══════════════════════════════════════════════════════════════

-- Beispielabfrage für die Auswertung (im SQL-Editor oder Backend):
--
-- SELECT
--   u.email,
--   a.arbeitsblatt,
--   a.antworten,
--   a.gespeichert_am
-- FROM arbeitsblatt_antworten a
-- JOIN auth.users u ON u.id = a.user_id
-- WHERE a.arbeitsblatt = 'java_musikplayer_v1'
-- ORDER BY u.email;


-- ══════════════════════════════════════════════════════════════
--  TESTDATEN (optional, zum Ausprobieren im SQL-Editor)
--  Nur ausführen, wenn du einen echten user_id-Wert zur Hand hast.
--  Den findest du unter: Authentication → Users → User-ID kopieren.
-- ══════════════════════════════════════════════════════════════

-- INSERT INTO arbeitsblatt_antworten (user_id, arbeitsblatt, antworten, gespeichert_am)
-- VALUES (
--   'DEINE-USER-UUID-HIER',
--   'java_musikplayer_v1',
--   '{"q1":"b","q2":"b","q3":"c","q4":"c","q5":"c","q6":"b","q8":"Die Methode setzt das Attribut spielt auf true und gibt eine Meldung auf der Konsole aus."}',
--   now()
-- );
