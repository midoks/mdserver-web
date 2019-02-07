CREATE TABLE `pl_hash_list` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `info_hash` varchar(40) NOT NULL,
  `length` bigint(20) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `info_hash` (`info_hash`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `pl_hash_file` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `pid` bigint(20)  NOT NULL,
  `name` text NOT NULL,
  `m3u8` varchar(40) NOT NULL,
  `length` bigint(20) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `pl_hash_queue` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `info_hash` varchar(40) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;