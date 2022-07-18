CREATE TABLE IF NOT EXISTS `web_logs` (
    `time` INTEGER,
    `ip` TEXT,
    `domain` TEXT,
    `server_name` TEXT,
    `method` TEXT,
    `status_code` INTEGER,
    `uri` TEXT,
    `body_length` INTEGER,
    `referer` TEXT DEFAULT "",
    `user_agent` TEXT,
    `is_spider` INTEGER DEFAULT 0,
    `protocol` TEXT,
    `request_time` INTEGER,
    `request_headers` TEXT DEFAULT "",
    `ip_list` TEXT DEFAULT "",
    `client_port` INTEGER DEFAULT -1
);

CREATE INDEX time_inx ON web_logs(`time`);
