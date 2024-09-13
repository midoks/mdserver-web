CREATE TABLE IF NOT EXISTS `dnsapi` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `type` TEXT,
  `val` TEXT,
  `remark` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `email` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `addr` TEXT,
  `remark` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `domain` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `domain` TEXT,
  `dnsapi_id` TEXT,
  `email` TEXT,
  `remark` TEXT,
  `addtime` TEXT
);

