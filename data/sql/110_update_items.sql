
ALTER TABLE `items` CHANGE `sid` `sid` SMALLINT UNSIGNED NOT NULL ,
CHANGE `cid` `cid` SMALLINT UNSIGNED NOT NULL 

ALTER TABLE `items` CHANGE `known_as` `known_as` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL 

ALTER TABLE `items` CHANGE `known_as` `known_as` VARCHAR( 1000 ) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
CHANGE `attributes` `attributes` VARCHAR( 1000 ) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
CHANGE `custom` `custom` BIT ( 1 ) NOT NULL DEFAULT '0'
