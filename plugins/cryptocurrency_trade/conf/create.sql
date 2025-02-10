CREATE TABLE IF NOT EXISTS `ct_xx1_xx2` (
  `addtime` BIGINT(20) not NULL,
  `open` float NOT NULL,
  `high` float NOT NULL,
  `low` float NOT NULL,
  `close` float NOT NULL,
  `vol` float NOT NULL,
  UNIQUE KEY `addtime` (`addtime`)
);
