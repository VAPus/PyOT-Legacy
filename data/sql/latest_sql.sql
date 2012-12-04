-- MySQL dump 10.13  Distrib 5.5.28, for debian-linux-gnu (x86_64)
--

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL DEFAULT '',
  `password` varchar(255) NOT NULL,
  `salt` varchar(40) NOT NULL DEFAULT '',
  `premdays` int(11) NOT NULL DEFAULT '0',
  `language` char(5) NOT NULL DEFAULT 'en_EN',
  `blocked` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'internal usage',
  `group_id` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'111','6216f8a75fd5bb3d5f22b6f9958cdede3fc086c2','',65535,'en_EN',0,1);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bans`
--

DROP TABLE IF EXISTS `bans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bans` (
  `ban_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `ban_type` tinyint(4) unsigned NOT NULL COMMENT '0 means ban_data = account_id, 1 means ban_data is playerId, 2 means ban_data = ip.',
  `ban_by` int(11) unsigned DEFAULT NULL,
  `ban_data` varchar(64) NOT NULL,
  `ban_reason` varchar(255) NOT NULL,
  `ban_expire` int(11) unsigned NOT NULL,
  PRIMARY KEY (`ban_id`),
  KEY `ban_by` (`ban_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bans`
--

LOCK TABLES `bans` WRITE;
/*!40000 ALTER TABLE `bans` DISABLE KEYS */;
/*!40000 ALTER TABLE `bans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `globals`
--

DROP TABLE IF EXISTS `globals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `globals` (
  `key` varchar(16) NOT NULL,
  `data` mediumblob NOT NULL,
  `type` varchar(16) NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `globals`
--

LOCK TABLES `globals` WRITE;
/*!40000 ALTER TABLE `globals` DISABLE KEYS */;
INSERT INTO `globals` VALUES ('objectStorage','€}q.','pickle'),('storage','{}','json');
/*!40000 ALTER TABLE `globals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `group_id` int(11) unsigned NOT NULL,
  `group_name` varchar(48) NOT NULL,
  `group_flags` text NOT NULL,
  PRIMARY KEY (`group_id`),
  KEY `group_name` (`group_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'Player','[\"SAVESELF\", \"HOUSE\", \"PREMIUM\", \"SPELLS\", \"SPEAK\", \"MOVE_ITEMS\", \"LOOT\", \"ATTACK\"]'),(2,'Tutor','[\"SAVESELF\", \"HOUSE\", \"PREMIUM\", \"SPELLS\", \"SPEAK\", \"MOVE_ITEMS\", \"LOOT\", \"ATTACK\"]'),(3,'Community Manager','[\"MUTE\", \"TELEPORT\", \"IMMUNE\", \"NO_EXHAUST\", \"IGNORED_BY_CREATURES\", \"TALK_ORANGE\", \"SPEED\", \"SAVESELF\", \"SPEAK\", \"MOVE_ITEMS\"]'),(4,'Gamemaster','[\"CREATEITEM\", \"TELEPORT\", \"SETHOUSEOWNER\", \"SAVEALL\", \"SAVESELF\", \"SPAWN\", \"RAID\", \"HOUSE\", \"KICK\", \"BAN\", \"MUTE\", \"PREMIUM\", \"SPELLS\", \"SPEAK\", \"SPEED\", \"MOVE_ITEMS\", \"LOOT\", \"INVISIBLE\", \"INFINATE_SOUL\", \"INFINATE_MANA\", \"INFINATE_HEALTH\", \"INFINATE_STAMINA\", \"ATTACK\", \"IGNORED_BY_CREATURES\", \"TALK_ORANGE\", \"TALK_RED\", \"IMMUNE\", \"NO_EXHAUST\"]'),(5,'God','[\"CREATEITEM\", \"TELEPORT\", \"SETHOUSEOWNER\", \"SAVEALL\", \"SAVESELF\", \"SPAWN\", \"RAID\", \"HOUSE\", \"MANAGESERVER\", \"MODIFYMAP\", \"KICK\", \"RELOAD\", \"BAN\", \"MUTE\", \"DEVELOPER\", \"PREMIUM\", \"SPELLS\", \"SPEAK\", \"SPEED\", \"MOVE_ITEMS\", \"LOOT\", \"INVISIBLE\", \"INFINATE_SOUL\", \"INFINATE_MANA\", \"INFINATE_HEALTH\", \"INFINATE_STAMINA\", \"ATTACK\", \"IGNORED_BY_CREATURES\", \"TALK_ORANGE\", \"TALK_RED\", \"IMMUNE\", \"NO_EXHAUST\"]'),(6,'Admin','[\"CREATEITEM\", \"TELEPORT\", \"SETHOUSEOWNER\", \"SAVEALL\", \"SAVESELF\", \"SPAWN\", \"RAID\", \"HOUSE\", \"MANAGESERVER\", \"MODIFYMAP\", \"KICK\", \"RELOAD\", \"BAN\", \"MUTE\", \"DEVELOPER\", \"PREMIUM\", \"SPELLS\", \"SPEAK\", \"SPEED\", \"MOVE_ITEMS\", \"LOOT\", \"INVISIBLE\", \"INFINATE_SOUL\", \"INFINATE_MANA\", \"INFINATE_HEALTH\", \"INFINATE_STAMINA\", \"ATTACK\", \"IGNORED_BY_CREATURES\", \"TALK_ORANGE\", \"TALK_RED\", \"IMMUNE\", \"NO_EXHAUST\"]');
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guild_invites`
--

DROP TABLE IF EXISTS `guild_invites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guild_invites` (
  `player_id` int(10) unsigned NOT NULL DEFAULT '0',
  `guild_id` int(10) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guild_invites`
--

LOCK TABLES `guild_invites` WRITE;
/*!40000 ALTER TABLE `guild_invites` DISABLE KEYS */;
/*!40000 ALTER TABLE `guild_invites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guild_ranks`
--

DROP TABLE IF EXISTS `guild_ranks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guild_ranks` (
  `guild_id` int(11) unsigned NOT NULL,
  `rank_id` int(6) unsigned NOT NULL,
  `title` varchar(64) NOT NULL,
  `permissions` int(11) unsigned NOT NULL,
  KEY `guild_id` (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guild_ranks`
--

LOCK TABLES `guild_ranks` WRITE;
/*!40000 ALTER TABLE `guild_ranks` DISABLE KEYS */;
/*!40000 ALTER TABLE `guild_ranks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guild_wars`
--

DROP TABLE IF EXISTS `guild_wars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guild_wars` (
  `war_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `guild_id` int(11) unsigned NOT NULL,
  `guild_id2` int(11) unsigned NOT NULL,
  `started` int(11) unsigned NOT NULL,
  `duration` int(11) unsigned NOT NULL,
  `frags` int(11) unsigned NOT NULL,
  `stakes` int(11) unsigned NOT NULL,
  `status` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 = invitation, 1 = rejected, 2 = accepted, 3 = cancelled, 4 = active, 5 = over',
  PRIMARY KEY (`war_id`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guild_wars`
--

LOCK TABLES `guild_wars` WRITE;
/*!40000 ALTER TABLE `guild_wars` DISABLE KEYS */;
/*!40000 ALTER TABLE `guild_wars` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guilds`
--

DROP TABLE IF EXISTS `guilds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guilds` (
  `guild_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `world_id` tinyint(8) unsigned NOT NULL,
  `name` varchar(64) NOT NULL,
  `created` int(11) unsigned NOT NULL,
  `motd` varchar(255) NOT NULL,
  `balance` int(11) unsigned NOT NULL,
  PRIMARY KEY (`guild_id`),
  KEY `world_id` (`world_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guilds`
--

LOCK TABLES `guilds` WRITE;
/*!40000 ALTER TABLE `guilds` DISABLE KEYS */;
INSERT INTO `guilds` VALUES (1,0,'Test guild',0,'Hello world',4294967295),(2,0,'Test guild 2',0,'Hello universe',4294967295);
/*!40000 ALTER TABLE `guilds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `houses`
--

DROP TABLE IF EXISTS `houses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `houses` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `owner` int(11) unsigned NOT NULL DEFAULT '0',
  `guild` int(8) unsigned NOT NULL DEFAULT '0',
  `paid` int(11) unsigned NOT NULL DEFAULT '0',
  `name` varchar(64) NOT NULL,
  `town` int(8) unsigned NOT NULL DEFAULT '0',
  `size` int(8) unsigned NOT NULL,
  `rent` int(11) unsigned NOT NULL,
  `data` mediumblob,
  `price` int(11) unsigned NOT NULL DEFAULT '0',
  `for_sale` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `houses`
--

LOCK TABLES `houses` WRITE;
/*!40000 ALTER TABLE `houses` DISABLE KEYS */;
INSERT INTO `houses` VALUES (1,0,0,0,'The W House',1,126,1000,'€}q(Uitemsq}q((MèMéKKtq]q(cgame.item\nItem\nq)q}qUitemIdq	Msbh)q\n}qUitemIdqMsbe(MèMéKKtq\r]q(h)q}qh	Msbh)q}qhMsbe(MèMéKKtq]q(h)q}qh	Msbh)q}qhMsbe(MêMèKK\0tq]q\Z(h)q}q(h	MÃU	containerqc_collections\ndeque\nq]qK†q Rq!ubh)q\"}q#(hMÃU	containerq$h]q%K†q&Rq\'ube(MèMéKKtq(]q)(h)q*}q+h	Msbh)q,}q-hMsbeuUguestsq.]q/Udoorsq0}q1U	subownersq2]q3u.',0,0),(2,0,0,0,'The Bear',1,193,100000,NULL,0,0),(3,0,0,0,'The School and Church',1,109,100000000,NULL,0,0),(4,0,0,0,'Island',1,18,10000000,NULL,0,0),(5,0,0,0,'Mini Flat I',1,50,10000,NULL,0,0),(6,0,0,0,'Mini Flat II',1,50,10000,NULL,0,0),(7,0,0,0,'Mini Flat III',1,50,10000,NULL,0,0),(8,0,0,0,'Mini Flat IV',1,50,10000,NULL,0,0),(9,0,0,0,'Stone Entrance I',1,40,10000,NULL,0,0),(10,0,0,0,'Stone Entrance II',1,28,10000,NULL,0,0),(11,0,0,0,'Stone Entrance III',1,28,10000,NULL,0,0),(12,0,0,0,'Yellow Flower I',1,18,10000,NULL,0,0),(13,0,0,0,'Yellow Flower II',1,18,10000,NULL,0,0),(14,0,0,0,'Yellow Flower III',1,18,10000,NULL,0,0),(15,0,0,0,'Temple House I',1,20,10000,NULL,0,0),(16,0,0,0,'Temple House II',1,20,10000,NULL,0,0),(17,0,0,0,'Temple House III',1,20,10000,NULL,0,0),(18,0,0,0,'City Side I',1,18,10000,NULL,0,0),(19,0,0,0,'City Side II',1,18,10000,NULL,0,0),(20,0,0,0,'City Side III',1,25,10000,NULL,0,0),(21,0,0,0,'City Side IV',1,20,10000,NULL,0,0),(22,0,0,0,'Sandland',1,132,100000,NULL,0,0),(23,0,0,0,'Desert Ground',1,15,10000,NULL,0,0),(24,0,0,0,'Desert Ground II',1,15,10000,NULL,0,0),(25,0,0,0,'Ezo TownHouse I',1,48,100000,NULL,0,0),(26,0,0,0,'Ezo TownHouse II',1,9,100000,NULL,0,0),(27,0,0,0,'Ezo TownHouse III',1,9,100000,NULL,0,0),(28,0,0,0,'Ezo TownHouse IV',1,40,100000,NULL,0,0),(29,0,0,0,'Ezo TownHouse V',1,40,100000,NULL,0,0);
/*!40000 ALTER TABLE `houses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `market_history`
--

DROP TABLE IF EXISTS `market_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `market_history` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `offer_id` int(11) unsigned NOT NULL,
  `player_id` int(11) unsigned NOT NULL,
  `amount` int(11) unsigned NOT NULL,
  `time` int(11) unsigned NOT NULL,
  `type` tinyint(2) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `market_history`
--

LOCK TABLES `market_history` WRITE;
/*!40000 ALTER TABLE `market_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `market_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `market_offers`
--

DROP TABLE IF EXISTS `market_offers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `market_offers` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `world_id` tinyint(8) unsigned NOT NULL,
  `market_id` int(11) unsigned NOT NULL,
  `player_id` int(11) unsigned NOT NULL,
  `item_id` smallint(11) unsigned NOT NULL,
  `amount` smallint(11) unsigned NOT NULL,
  `created` int(11) unsigned NOT NULL,
  `price` int(11) NOT NULL,
  `anonymous` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `type` tinyint(4) unsigned NOT NULL COMMENT '0 = over, 1 = sale, 2 =\nbuy',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `market_offers`
--

LOCK TABLES `market_offers` WRITE;
/*!40000 ALTER TABLE `market_offers` DISABLE KEYS */;
/*!40000 ALTER TABLE `market_offers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_guild`
--

DROP TABLE IF EXISTS `player_guild`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player_guild` (
  `player_id` int(11) unsigned NOT NULL,
  `guild_id` int(11) unsigned NOT NULL,
  `guild_rank` int(6) unsigned NOT NULL DEFAULT '0',
  `guild_title` varchar(255) NOT NULL DEFAULT '',
  `joined` int(10) NOT NULL,
  KEY `guild_id` (`guild_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_guild`
--

LOCK TABLES `player_guild` WRITE;
/*!40000 ALTER TABLE `player_guild` DISABLE KEYS */;
/*!40000 ALTER TABLE `player_guild` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_skills`
--

DROP TABLE IF EXISTS `player_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player_skills` (
  `player_id` int(11) unsigned NOT NULL,
  `fist` int(11) unsigned NOT NULL DEFAULT '10',
  `fist_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `sword` int(11) unsigned NOT NULL DEFAULT '10',
  `sword_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `club` int(11) unsigned NOT NULL DEFAULT '10',
  `club_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `axe` int(11) unsigned NOT NULL DEFAULT '10',
  `axe_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `distance` int(11) unsigned NOT NULL DEFAULT '10',
  `distance_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `shield` int(11) unsigned NOT NULL DEFAULT '10',
  `shield_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `fishing` int(11) unsigned NOT NULL DEFAULT '0',
  `fishing_tries` int(11) unsigned NOT NULL DEFAULT '0',
  `custom` tinytext COMMENT 'Might be NULL, JSON dict ID -> skilltries',
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_skills`
--

LOCK TABLES `player_skills` WRITE;
/*!40000 ALTER TABLE `player_skills` DISABLE KEYS */;
INSERT INTO `player_skills` VALUES (2,10,0,10,0,10,0,10,0,10,0,10,0,0,0,NULL);
/*!40000 ALTER TABLE `player_skills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `players` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `world_id` tinyint(8) unsigned NOT NULL DEFAULT '0',
  `group_id` int(11) NOT NULL DEFAULT '1',
  `account_id` int(11) NOT NULL DEFAULT '0',
  `vocation` tinyint(8) unsigned NOT NULL DEFAULT '0',
  `health` decimal(65,0) unsigned NOT NULL DEFAULT '150',
  `experience` decimal(65,0) unsigned NOT NULL DEFAULT '0',
  `lookbody` tinyint(11) unsigned NOT NULL DEFAULT '0',
  `lookfeet` tinyint(11) unsigned NOT NULL DEFAULT '0',
  `lookhead` tinyint(11) unsigned NOT NULL DEFAULT '0',
  `looklegs` tinyint(11) unsigned NOT NULL DEFAULT '0',
  `looktype` smallint(11) unsigned NOT NULL DEFAULT '136',
  `lookaddons` tinyint(11) unsigned NOT NULL DEFAULT '0',
  `lookmount` smallint(11) unsigned NOT NULL DEFAULT '0',
  `mana` decimal(65,0) unsigned NOT NULL DEFAULT '0',
  `manaspent` decimal(65,0) unsigned NOT NULL DEFAULT '0',
  `soul` int(10) unsigned NOT NULL DEFAULT '0',
  `town_id` int(11) NOT NULL DEFAULT '0',
  `posx` int(11) NOT NULL DEFAULT '0',
  `posy` int(11) NOT NULL DEFAULT '0',
  `posz` int(11) NOT NULL DEFAULT '0',
  `instanceId` mediumint(5) DEFAULT NULL,
  `sex` int(11) NOT NULL DEFAULT '0',
  `skull` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `stamina` decimal(65,0) unsigned NOT NULL DEFAULT '151200000' COMMENT 'stored in miliseconds',
  `marriage` int(10) unsigned NOT NULL DEFAULT '0',
  `lastlogin` int(11) unsigned NOT NULL DEFAULT '0',
  `online` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `conditions` blob,
  `balance` decimal(65,0) unsigned NOT NULL DEFAULT '0',
  `storage` mediumblob,
  `depot` mediumblob,
  `inventory` mediumblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `account_id` (`account_id`),
  KEY `group_id` (`group_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `players`
--

LOCK TABLES `players` WRITE;
/*!40000 ALTER TABLE `players` DISABLE KEYS */;
INSERT INTO `players` VALUES (2,'Test',0,6,1,1,15000,717601,68,76,78,39,302,0,0,60000,60000,100,1,1000,1000,7,NULL,1,0,151200000,0,0,0,NULL,0,NULL,'','');
/*!40000 ALTER TABLE `players` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pvp_deaths`
--

DROP TABLE IF EXISTS `pvp_deaths`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pvp_deaths` (
  `death_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `killer_id` int(11) unsigned NOT NULL,
  `victim_id` int(11) unsigned NOT NULL,
  `unjust` tinyint(1) NOT NULL,
  `time` int(11) unsigned NOT NULL,
  `revenged` tinyint(1) NOT NULL DEFAULT '0',
  `war_id` int(11) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`death_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pvp_deaths`
--

LOCK TABLES `pvp_deaths` WRITE;
/*!40000 ALTER TABLE `pvp_deaths` DISABLE KEYS */;
/*!40000 ALTER TABLE `pvp_deaths` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-12-04 20:56:42
