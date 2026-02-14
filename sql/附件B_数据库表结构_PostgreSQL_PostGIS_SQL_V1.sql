-- 附件B：数据库表结构草案（PostgreSQL + PostGIS）
-- Version: V1
-- Encoding: UTF-8

BEGIN;

-- 0) Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) Enums
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'business_type_enum') THEN
    CREATE TYPE business_type_enum AS ENUM (
      'tea', 'icecream', 'dessert', 'bakery', 'meatpie', 'noodle_premium'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_status_enum') THEN
    CREATE TYPE project_status_enum AS ENUM ('active', 'archived');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'site_status_enum') THEN
    CREATE TYPE site_status_enum AS ENUM (
      'pending', 'evaluating', 'field_check', 'approved', 'rejected'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'source_type_enum') THEN
    CREATE TYPE source_type_enum AS ENUM ('manual', 'import', 'amap_poi');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'route_mode_enum') THEN
    CREATE TYPE route_mode_enum AS ENUM ('walk', 'drive');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_enum') THEN
    CREATE TYPE recommendation_enum AS ENUM ('recommend', 'caution', 'reject');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'report_type_enum') THEN
    CREATE TYPE report_type_enum AS ENUM ('full', 'brief');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role_enum') THEN
    CREATE TYPE user_role_enum AS ENUM ('admin', 'manager', 'analyst', 'viewer');
  END IF;
END $$;

-- 2) Users & Permissions
CREATE TABLE IF NOT EXISTS users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  email           TEXT NOT NULL UNIQUE,
  role            user_role_enum NOT NULL DEFAULT 'viewer',
  status          TEXT NOT NULL DEFAULT 'active',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id                  BIGSERIAL PRIMARY KEY,
  user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
  module              TEXT NOT NULL,
  action              TEXT NOT NULL,
  request_meta_json   JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3) Projects & Sites
CREATE TABLE IF NOT EXISTS projects (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  city_code       TEXT NOT NULL,
  business_type   business_type_enum NOT NULL,
  status          project_status_enum NOT NULL DEFAULT 'active',
  owner_user_id   UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS site_candidates (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  address         TEXT NOT NULL,
  -- 高德坐标系（GCJ-02）可先按 WGS84 存 geometry；后续可增加 srid 字段记录来源
  location_gcj    geometry(Point, 4326) NOT NULL,
  source_type     source_type_enum NOT NULL DEFAULT 'manual',
  area_sqm        NUMERIC(10,2),
  rent_monthly    NUMERIC(12,2),
  status          site_status_enum NOT NULL DEFAULT 'pending',
  remarks         TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS competitors (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_name      TEXT NOT NULL,
  store_name      TEXT,
  category        TEXT NOT NULL,
  price_band      TEXT,
  address         TEXT,
  location_gcj    geometry(Point, 4326),
  source          TEXT NOT NULL DEFAULT 'amap',
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4) Amap Caches
CREATE TABLE IF NOT EXISTS amap_poi_cache (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_hash      TEXT NOT NULL UNIQUE,
  query_json      JSONB NOT NULL,
  response_json   JSONB NOT NULL,
  expires_at      TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS amap_route_cache (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  origin          TEXT NOT NULL,
  destination     TEXT NOT NULL,
  mode            route_mode_enum NOT NULL,
  distance_m      INTEGER,
  duration_s      INTEGER,
  response_json   JSONB NOT NULL,
  expires_at      TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(origin, destination, mode)
);

-- 5) Scoring & Model
CREATE TABLE IF NOT EXISTS score_templates (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_type   business_type_enum NOT NULL,
  version         TEXT NOT NULL,
  weights_json    JSONB NOT NULL,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (business_type, version)
);

CREATE TABLE IF NOT EXISTS site_scores (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_candidate_id       UUID NOT NULL REFERENCES site_candidates(id) ON DELETE CASCADE,
  template_id             UUID NOT NULL REFERENCES score_templates(id) ON DELETE RESTRICT,
  total_score             NUMERIC(6,2) NOT NULL,
  dimension_scores_json   JSONB NOT NULL,
  risk_penalty            NUMERIC(6,2) NOT NULL DEFAULT 0,
  recommendation          recommendation_enum NOT NULL,
  explanation_text        TEXT,
  scored_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS field_checks (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_candidate_id       UUID NOT NULL REFERENCES site_candidates(id) ON DELETE CASCADE,
  traffic_observation     TEXT,
  visibility_observation  TEXT,
  rival_observation       TEXT,
  risk_notes              TEXT,
  photos_json             JSONB NOT NULL DEFAULT '[]'::jsonb,
  checker_user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
  checked_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6) Report & Workflow
CREATE TABLE IF NOT EXISTS reports (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  site_candidate_id   UUID NOT NULL REFERENCES site_candidates(id) ON DELETE CASCADE,
  report_type         report_type_enum NOT NULL,
  report_url          TEXT,
  snapshot_json       JSONB NOT NULL DEFAULT '{}'::jsonb,
  generated_by        UUID REFERENCES users(id) ON DELETE SET NULL,
  generated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workflow_logs (
  id                BIGSERIAL PRIMARY KEY,
  entity_type       TEXT NOT NULL, -- site/report/project
  entity_id         UUID NOT NULL,
  action            TEXT NOT NULL,
  from_status       TEXT,
  to_status         TEXT,
  operator_user_id  UUID REFERENCES users(id) ON DELETE SET NULL,
  note              TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7) Indexes
CREATE INDEX IF NOT EXISTS idx_projects_city_business ON projects(city_code, business_type);
CREATE INDEX IF NOT EXISTS idx_site_candidates_project_status ON site_candidates(project_id, status);
CREATE INDEX IF NOT EXISTS idx_site_scores_site_time ON site_scores(site_candidate_id, scored_at DESC);
CREATE INDEX IF NOT EXISTS idx_competitors_category ON competitors(category);
CREATE INDEX IF NOT EXISTS idx_reports_project_site ON reports(project_id, site_candidate_id);
CREATE INDEX IF NOT EXISTS idx_workflow_entity ON workflow_logs(entity_type, entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON audit_logs(user_id, created_at DESC);

-- Spatial indexes
CREATE INDEX IF NOT EXISTS idx_site_candidates_geom ON site_candidates USING GIST(location_gcj);
CREATE INDEX IF NOT EXISTS idx_competitors_geom ON competitors USING GIST(location_gcj);

-- 8) Updated_at trigger (optional)
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_projects_updated_at ON projects;
CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_site_candidates_updated_at ON site_candidates;
CREATE TRIGGER trg_site_candidates_updated_at
BEFORE UPDATE ON site_candidates
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;

-- End of file
