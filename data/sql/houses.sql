CREATE TABLE IF NOT EXISTS `houses` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `owner` int(11) unsigned NOT NULL DEFAULT '0',
  `guild` int(8) unsigned NOT NULL DEFAULT '0',
  `paid` int(11) unsigned NOT NULL DEFAULT '0',
  `name` varchar(64) NOT NULL,
  `town` int(8) unsigned NOT NULL DEFAULT '0',
  `size` int(8) unsigned NOT NULL,
  `rent` int(11) unsigned NOT NULL,
  `data` blob,
  `price` int(11) unsigned NOT NULL DEFAULT '0',
  `for_sale` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
INSERT INTO `houses` (`id`,`name`,`town`,`size`,`rent`) VALUES('1', 'The W House', '1', '126', '1000');