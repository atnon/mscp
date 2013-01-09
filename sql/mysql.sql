CREATE TABLE IF NOT EXISTS `log` (
  `id` int(45) unsigned NOT NULL AUTO_INCREMENT,
  `date` varchar(45) NOT NULL,
  `time` varchar(45) NOT NULL,
  `level` enum('INFO','WARNING','SEVERE','UNKNOWN') NOT NULL,
  `message` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

