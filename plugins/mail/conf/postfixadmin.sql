CREATE TABLE IF NOT EXISTS `domain` (
    `domain` varchar(255) NOT NULL,
    `a_record` TEXT DEFAULT "",
    `created` datetime NOT NULL,
    `active` tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (`domain`)
);

CREATE TABLE IF NOT EXISTS `mailbox` (
    `username` varchar(255) NOT NULL,
    `password` varchar(255) NOT NULL,
    `password_encode` varchar(255) NOT NULL,
    `full_name` varchar(255) NOT NULL,
    `is_admin` tinyint(1) NOT NULL DEFAULT 0,
    `maildir` varchar(255) NOT NULL,
    `quota` bigint(20) NOT NULL DEFAULT 0,
    `local_part` varchar(255) NOT NULL,
    `domain` varchar(255) NOT NULL,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `active` tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (`username`)
);

CREATE TABLE IF NOT EXISTS `alias` (
    `address` varchar(255) NOT NULL,
    `goto` text NOT NULL,
    `domain` varchar(255) NOT NULL,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `active` tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (`address`)
);

CREATE TABLE IF NOT EXISTS `alias_domain` (
    `alias_domain` varchar(255) NOT NULL,
    `target_domain` varchar(255) NOT NULL,
    `created` datetime NOT NULL,
    `modified` datetime NOT NULL,
    `active` tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (`alias_domain`)
);