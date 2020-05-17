CREATE TABLE `search_hash` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `info_hash` varchar(40) NOT NULL,
  `category` varchar(20) NOT NULL,
  `data_hash` varchar(32) NOT NULL,
  `name` varchar(255) NOT NULL,
  `extension` varchar(20) NOT NULL,
  `classified` tinyint(1) NOT NULL,
  `source_ip` varchar(20) DEFAULT NULL,
  `tagged` tinyint(1) NOT NULL,
  `length` bigint(20) NOT NULL,
  `create_time` datetime NOT NULL,
  `last_seen` datetime NOT NULL,
  `requests` int(10) unsigned NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `is_dmca` tinyint(4) NULL DEFAULT 0,
  `is_has` tinyint(4) NULL DEFAULT 1,
  `creator` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `info_hash` (`info_hash`),
  KEY `search_hash_uniq` (`tagged`),
  KEY `create_time` (`create_time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE `search_filelist` (
  `info_hash` varchar(40) NOT NULL,
  `file_list` longtext NOT NULL,
  PRIMARY KEY (`info_hash`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


CREATE TABLE `search_statusreport` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `new_hashes` int(11) NOT NULL,
  `total_requests` int(11) NOT NULL,
  `valid_requests` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `search_statusreport_uniq` (`date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- sphinx delta need  ---
CREATE TABLE `sph_counter` (
  `counter_id` int(11) NOT NULL COMMENT '标识不同的数据表',
  `max_doc_id` int(11) NOT NULL COMMENT '每个索引表的最大ID,会实时更新',
  PRIMARY KEY (`counter_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;