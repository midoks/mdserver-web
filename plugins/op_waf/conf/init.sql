PRAGMA synchronous = 0;
PRAGMA page_size = 4096;
PRAGMA journal_mode = wal;
PRAGMA journal_size_limit = 1073741824;

CREATE TABLE IF NOT EXISTS `logs` (
    `time` INTEGER,
    `ip` TEXT,
    `domain` TEXT,
    `server_name` TEXT,
    `method` TEXT,
    `status_code` INTEGER,
    `user_agent` TEXT,
    `uri` TEXT,
    `rule_name` TEXT,
    `reason` TEXT
);
