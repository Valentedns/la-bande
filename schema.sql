-- Schéma de la base de données de La Bande.
-- "IF NOT EXISTS" permet de relancer ce script sans effacer les données.
-- Montants en centimes (12,50 EUR = 1250). Dates au format ISO (2026-10-03, 2026-10-03T20:00).

-- ===== Comptes et groupes =====
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS friend_groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    invite_code TEXT    NOT NULL UNIQUE,
    created_by  INTEGER NOT NULL REFERENCES users(id),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memberships (
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id  INTEGER NOT NULL REFERENCES friend_groups(id) ON DELETE CASCADE,
    role      TEXT    NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'member')),
    joined_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, group_id)
);

-- ===== Calendrier des dispos (personnel, visible dans tous ses groupes) =====
CREATE TABLE IF NOT EXISTS availabilities (
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day        TEXT    NOT NULL,
    status     TEXT    NOT NULL CHECK (status IN ('free', 'maybe', 'busy')),
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, day)
);

-- ===== Lieux et notes =====
CREATE TABLE IF NOT EXISTS places (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id   INTEGER NOT NULL REFERENCES friend_groups(id) ON DELETE CASCADE,
    name       TEXT    NOT NULL,
    address    TEXT,
    category   TEXT    NOT NULL DEFAULT 'autre'
               CHECK (category IN ('restaurant', 'bar', 'soiree', 'activite', 'vacances', 'autre')),
    latitude   REAL    NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude  REAL    NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS place_ratings (
    place_id   INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score      INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
    verdict    TEXT    NOT NULL CHECK (verdict IN ('qg', 'a_refaire', 'bof', 'a_eviter')),
    comment    TEXT    CHECK (comment IS NULL OR length(comment) <= 500),
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (place_id, user_id)
);

-- ===== Sorties =====
CREATE TABLE IF NOT EXISTS outings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id    INTEGER NOT NULL REFERENCES friend_groups(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    description TEXT,
    category    TEXT    NOT NULL DEFAULT 'autre'
                CHECK (category IN ('restaurant', 'bar', 'soiree', 'activite', 'vacances', 'autre')),
    place_id    INTEGER REFERENCES places(id) ON DELETE SET NULL,
    starts_at   TEXT    NOT NULL,
    ends_at     TEXT,
    status      TEXT    NOT NULL DEFAULT 'proposed'
                CHECK (status IN ('proposed', 'confirmed', 'done', 'cancelled')),
    created_by  INTEGER NOT NULL REFERENCES users(id),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outing_responses (
    outing_id  INTEGER NOT NULL REFERENCES outings(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    response   TEXT    NOT NULL CHECK (response IN ('yes', 'maybe', 'no')),
    updated_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (outing_id, user_id)
);

CREATE TABLE IF NOT EXISTS date_proposals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    outing_id   INTEGER NOT NULL REFERENCES outings(id) ON DELETE CASCADE,
    proposed_by INTEGER NOT NULL REFERENCES users(id),
    starts_at   TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (outing_id, starts_at)
);

CREATE TABLE IF NOT EXISTS date_proposal_votes (
    proposal_id INTEGER NOT NULL REFERENCES date_proposals(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (proposal_id, user_id)
);

-- ===== Dépenses (Tricount intégré) =====
CREATE TABLE IF NOT EXISTS expenses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id     INTEGER NOT NULL REFERENCES friend_groups(id) ON DELETE CASCADE,
    outing_id    INTEGER REFERENCES outings(id) ON DELETE SET NULL,
    payer_id     INTEGER NOT NULL REFERENCES users(id),
    description  TEXT    NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    split_mode   TEXT    NOT NULL DEFAULT 'equal' CHECK (split_mode IN ('equal', 'custom')),
    spent_on     TEXT    NOT NULL,
    created_by   INTEGER NOT NULL REFERENCES users(id),
    created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expense_shares (
    expense_id  INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    share_cents INTEGER NOT NULL CHECK (share_cents >= 0),
    PRIMARY KEY (expense_id, user_id)
);

CREATE TABLE IF NOT EXISTS settlements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id     INTEGER NOT NULL REFERENCES friend_groups(id) ON DELETE CASCADE,
    from_user_id INTEGER NOT NULL REFERENCES users(id),
    to_user_id   INTEGER NOT NULL REFERENCES users(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    paid_on      TEXT    NOT NULL,
    created_at   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (from_user_id <> to_user_id)
);

-- ===== Album photo =====
CREATE TABLE IF NOT EXISTS photos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    outing_id     INTEGER NOT NULL REFERENCES outings(id) ON DELETE CASCADE,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    stored_name   TEXT    NOT NULL UNIQUE,   -- nom aléatoire (uuid4) dans uploads/
    original_name TEXT,
    caption       TEXT    CHECK (caption IS NULL OR length(caption) <= 200),
    is_cover      INTEGER NOT NULL DEFAULT 0 CHECK (is_cover IN (0, 1)),
    created_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ===== Bonus : fil de discussion =====
CREATE TABLE IF NOT EXISTS outing_comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    outing_id  INTEGER NOT NULL REFERENCES outings(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    content    TEXT    NOT NULL CHECK (length(content) BETWEEN 1 AND 500),
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ===== Index pour accélérer les recherches fréquentes =====
CREATE INDEX IF NOT EXISTS idx_outings_group    ON outings(group_id, starts_at);
CREATE INDEX IF NOT EXISTS idx_expenses_group   ON expenses(group_id);
CREATE INDEX IF NOT EXISTS idx_places_group     ON places(group_id);
CREATE INDEX IF NOT EXISTS idx_photos_outing    ON photos(outing_id);
CREATE INDEX IF NOT EXISTS idx_availabilities_d ON availabilities(day);
