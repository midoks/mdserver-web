CREATE TABLE IF NOT EXISTS `config` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `mysql_root` TEXT
);

INSERT INTO `config` (`id`, `mysql_root`) VALUES (1, 'admin');

CREATE TABLE IF NOT EXISTS `databases` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `name` TEXT,
  `username` TEXT,
  `password` TEXT,
  `accept` TEXT,
  `rw` TEXT DEFAULT 'rw',
  `ps` TEXT,
  `addtime` TEXT
);
-- ALTER TABLE `databases` ADD COLUMN `rw` TEXT DEFAULT 'rw';

CREATE TABLE IF NOT EXISTS `master_replication_user` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `username` TEXT,
  `password` TEXT,
  `accept` TEXT,
  `ps` TEXT,
  `addtime` TEXT
);

-- 从库配置主库的[ssh private key]
-- drop table `slave_id_rsa`;
CREATE TABLE IF NOT EXISTS `slave_id_rsa` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `ip` TEXT,
  `port` TEXT,
  `user` TEXT,
  `db_user` TEXT,
  `id_rsa` TEXT,
  `ps` TEXT,
  `addtime` TEXT
);

-- 从库配置主库的[user]
-- drop table `slave_user`;
CREATE TABLE IF NOT EXISTS `slave_sync_user` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `ip` TEXT,
  `port` TEXT,
  `user` TEXT,
  `pass` TEXT,
  `mode` TEXT,
  `cmd` TEXT,
  `db` TEXT,
  `addtime` TEXT
);
ALTER TABLE `slave_sync_user` ADD COLUMN `db` TEXT DEFAULT '';


