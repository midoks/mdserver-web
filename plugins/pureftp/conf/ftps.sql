CREATE TABLE IF NOT EXISTS `ftps` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `name` TEXT,
  `password` TEXT,
  `path` TEXT,
  `status` TEXT,
  `ps` TEXT,
  `addtime` TEXT
);