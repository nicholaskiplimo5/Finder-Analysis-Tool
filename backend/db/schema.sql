-- Applied automatically by the postgres container on first init
-- (mounted into /docker-entrypoint-initdb.d).

CREATE TABLE IF NOT EXISTS ticks (
    symbol TEXT NOT NULL,
    epoch  BIGINT NOT NULL,
    quote  NUMERIC NOT NULL,
    digit  SMALLINT NOT NULL CHECK (digit BETWEEN 0 AND 9),
    PRIMARY KEY (symbol, epoch)
);

-- PRIMARY KEY (symbol, epoch) already backs an index with this column order,
-- satisfying range scans of the form "symbol = X AND epoch BETWEEN a AND b".

CREATE TABLE IF NOT EXISTS symbol_meta (
    symbol     TEXT PRIMARY KEY,
    pip_size   NUMERIC NOT NULL,
    decimals   SMALLINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
