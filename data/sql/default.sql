
CREATE TABLE IF NOT EXISTS `backup` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` INTEGER,
  `name` TEXT,
  `pid` INTEGER,
  `filename` TEXT,
  `size` INTEGER,
  `add_time` TEXT
);

CREATE TABLE IF NOT EXISTS `binding` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `domain` TEXT,
  `path` TEXT,
  `port` INTEGER,
  `add_time` TEXT
);


CREATE TABLE IF NOT EXISTS `crontab` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `type` TEXT,
  `where1` TEXT,
  `where_hour` INTEGER,
  `where_minute` INTEGER,
  `echo` TEXT,
  `status` INTEGER DEFAULT '1',
  `save` INTEGER DEFAULT '3',
  `backup_to` TEXT DEFAULT 'off', 
  `sname` TEXT,
  `sbody` TEXT,
  'stype' TEXT,
  `url_address` TEXT,
  `add_time` TEXT,
  `update_time` TEXT
);

CREATE TABLE IF NOT EXISTS `firewall` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `port` TEXT,
  `protocol` TEXT DEFAULT 'tcp',
  `ps` TEXT,
  `add_time` TEXT,
  `update_time` TEXT
);

ALTER TABLE `firewall` ADD COLUMN `protocol` TEXT DEFAULT 'tcp';

INSERT INTO `firewall` (`id`, `port`, `protocol`, `ps`, `add_time`) VALUES
(1, '80',  'tcp','网站默认端口', '0000-00-00 00:00:00','0000-00-00 00:00:00'),
(2, '443', 'tcp/udp', 'HTTPS', '0000-00-00 00:00:00','0000-00-00 00:00:00');



CREATE TABLE IF NOT EXISTS `logs` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `type` TEXT,
  `log` TEXT,
  `uid` INTEGER DEFAULT '1',
  `add_time` TEXT
);

CREATE TABLE IF NOT EXISTS `sites` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `path` TEXT,
  `status` TEXT,
  `index` TEXT,
  `type_id` INTEGER,
  `ps` TEXT,
  `edate` TEXT,
  `ssl_effective_date` TEXT,
  `ssl_expiration_date` TEXT,
  `add_time` TEXT,
  `update_time` TEXT
);

CREATE TABLE IF NOT EXISTS `site_types` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT
);

CREATE TABLE IF NOT EXISTS `domain` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `pid` INTEGER,
  `name` TEXT,
  `port` INTEGER,
  `add_time` TEXT
);

CREATE TABLE IF NOT EXISTS `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `password` TEXT,
  `login_ip` TEXT,
  `login_time` TEXT,
  `phone` TEXT,
  `email` TEXT,
  `add_time` INTEGER,
  `update_time` INTEGER
);

CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` 			TEXT,
  `type`			TEXT,
  `start` 	  INTEGER,
  `end` 	    INTEGER,
  `cmd` 	    TEXT,
  `status`    INTEGER,
  `add_time`  INTEGER
);

CREATE TABLE IF NOT EXISTS `temp_login` (
  `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
  `token` REAL,
  `salt`  REAL,
  `state` INTEGER,
  `login_time`  INTEGER,
  `login_addr`  REAL,
  `logout_time` INTEGER,
  `expire`  INTEGER,
  `add_time` INTEGER
);

CREATE TABLE IF NOT EXISTS `panel` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `title` TEXT,
  `url` TEXT,
  `username` TEXT,
  `password` TEXT,
  `click` INTEGER,
  `add_time` INTEGER
);

CREATE TABLE IF NOT EXISTS `option` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `type` TEXT,
  `value` TEXT
);

CREATE UNIQUE INDEX name_idx ON option(name);
