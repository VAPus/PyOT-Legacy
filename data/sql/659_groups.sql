CREATE TABLE `groups` (
`group_id` INT( 11 ) UNSIGNED NOT NULL ,
`group_name` VARCHAR( 48 ) NOT NULL ,
`group_flags` TEXT NOT NULL ,
PRIMARY KEY ( `group_id` ) ,
INDEX ( `group_name` )
) ENGINE = InnoDB;

INSERT INTO `groups` VALUES(1, 'Player', '["SAVESELF", "HOUSE", "PREMIUM", "SPELLS", "SPEAK", "MOVE_ITEMS", "LOOT", "ATTACK"]')