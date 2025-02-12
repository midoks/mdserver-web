CREATE TABLE IF NOT EXISTS `ct_order_list` (
  `id` BIGINT(20) not NULL,
  'strategy_name' varchar(50) NULL,
  `symbol` varchar(50) NOT NULL,
  `fee` float NOT NULL,
  `price` float NOT NULL,
  `closing_price` float NOT NULL comment '',
  `profit` float NOT NULL,
  `source` TEXT,
  `addtime` BIGINT(20) not NULL
);
