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


CREATE INDEX time_idx ON logs(`time`);
CREATE INDEX ip_idx ON logs (`ip`);
CREATE INDEX uri_idx ON logs (`uri`);
CREATE INDEX method_idx ON logs (`method`);
CREATE INDEX server_name_idx ON logs (`server_name`);
CREATE INDEX status_code_idx ON logs (`status_code`);
CREATE INDEX all_union_idx ON logs (`status_code`, `time`, `ip`, `domain`, `server_name`, `method`, `uri`);

