CREATE TABLE IF NOT EXISTS `houses` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `owner` INT(11) UNSIGNED NOT NULL DEFAULT '0',
  `guild` INT(8) UNSIGNED NOT NULL DEFAULT '0',
  `paid` INT(11) UNSIGNED NOT NULL DEFAULT '0',
  `name` VARCHAR(64) NOT NULL,
  `town` INT(8) UNSIGNED NOT NULL DEFAULT '0',
  `size` INT(8) UNSIGNED NOT NULL,
  `rent` INT(11) UNSIGNED NOT NULL,
  `data` MEDIUMBLOB,
  `price` INT(11) UNSIGNED NOT NULL DEFAULT '0',
  `for_sale` tinyint(1) UNSIGNED NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;
INSERT INTO `houses` (`id`,`name`,`town`,`size`,`rent`) VALUES('1', 'The W House', '1', '126', '1000'),('2', 'The Bear', '1', '193', '100000'),('3', 'The School and Church', '1', '109', '100000000'),('4', 'Island', '1', '18', '10000000'),('5', 'Mini Flat I', '1', '50', '10000'),('6', 'Mini Flat II', '1', '50', '10000'),('7', 'Mini Flat III', '1', '50', '10000'),('8', 'Mini Flat IV', '1', '50', '10000'),('9', 'Stone Entrance I', '1', '40', '10000'),('10', 'Stone Entrance II', '1', '28', '10000'),('11', 'Stone Entrance III', '1', '28', '10000'),('12', 'Yellow Flower I', '1', '18', '10000'),('13', 'Yellow Flower II', '1', '18', '10000'),('14', 'Yellow Flower III', '1', '18', '10000'),('15', 'Temple House I', '1', '20', '10000'),('16', 'Temple House II', '1', '20', '10000'),('17', 'Temple House III', '1', '20', '10000'),('18', 'City Side I', '1', '18', '10000'),('19', 'City Side II', '1', '18', '10000'),('20', 'City Side III', '1', '25', '10000'),('21', 'City Side IV', '1', '20', '10000'),('22', 'Sandland', '1', '132', '100000'),('23', 'Desert Ground', '1', '15', '10000'),('24', 'Desert Ground II', '1', '15', '10000'),('25', 'Ezo TownHouse I', '1', '48', '100000'),('26', 'Ezo TownHouse II', '1', '9', '100000'),('27', 'Ezo TownHouse III', '1', '9', '100000'),('28', 'Ezo TownHouse IV', '1', '40', '100000'),('29', 'Ezo TownHouse V', '1', '40', '100000');