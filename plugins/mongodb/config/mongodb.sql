CREATE TABLE IF NOT EXISTS `config` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `mg_root` TEXT
);

INSERT INTO `config` (`id`, `mg_root`) VALUES (1, 'mg_root');

CREATE TABLE IF NOT EXISTS `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `username` TEXT,
  `password` TEXT,
  `role` TEXT DEFAULT '',
  `ps` TEXT,
  `addtime` TEXT
);

