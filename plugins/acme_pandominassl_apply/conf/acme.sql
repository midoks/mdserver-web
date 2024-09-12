CREATE TABLE IF NOT EXISTS `dnsapi` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `val` TEXT,
  `mark` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `email` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `addr` TEXT,
  `mark` TEXT,
  `addtime` TEXT
);

CREATE TABLE IF NOT EXISTS `domain` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `domain` TEXT,
  `email` TEXT,
  `dnsapi_id` TEXT,
  `mark` TEXT,
  `addtime` TEXT
);

