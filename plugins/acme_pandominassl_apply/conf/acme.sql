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
  `effective_date` TEXT,
  `expiration_date` TEXT,
  `error` TEXT,
  `status` INTEGER default '0',
  `addtime` TEXT
);

-- ALTER TABLE `domain` ADD COLUMN `effective_date` TEXT DEFAULT '';
-- ALTER TABLE `domain` ADD COLUMN `expiration_date` TEXT DEFAULT '';
-- ALTER TABLE `domain` ADD COLUMN `error` TEXT DEFAULT '';
-- ALTER TABLE `domain` ADD COLUMN `status` INTEGER DEFAULT '0';
