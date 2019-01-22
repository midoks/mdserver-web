CREATE TABLE `download_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `info_hash` varchar(40) NOT NULL,
  `data_hash` varchar(32) NOT NULL,
  `name` varchar(255) NOT NULL,
  `length` bigint(20) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `info_hash` (`info_hash`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;