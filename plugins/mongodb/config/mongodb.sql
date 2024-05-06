CREATE TABLE IF NOT EXISTS `config` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `mg_root` TEXT
);

INSERT INTO `config` (`id`, `mg_root`) VALUES (1, 'mg_root');


CREATE TABLE IF NOT EXISTS `databases` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `username` TEXT,
  `password` TEXT,
  `accept` TEXT,
  `rw` TEXT DEFAULT 'rw',
  `ps` TEXT,
  `addtime` TEXT
);

