CREATE DATABASE delibot;

USE delibot;

CREATE TABLE IF NOT EXISTS `exraids` (
  `server_id` varchar(25) DEFAULT NULL,
  `channel_id` varchar(25) DEFAULT NULL,
  `message_id` varchar(25) DEFAULT NULL,
  `user_id` varchar(25) DEFAULT NULL,
  `author` tinytext,
  `pokemon` varchar(20) DEFAULT NULL,
  `time` text,
  `day` text,
  `location` text,
  `valor` text,
  `mystic` text,
  `instinct` text,
  `harmony` int(11) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `gyms` (
  `server_id` varchar(25) DEFAULT NULL,
  `name` tinytext,
  `lat` tinytext,
  `lon` tinytext
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `languages` (
  `language` varchar(2) DEFAULT NULL,
  `raid_time` text,
  `raid_location` text,
  `raid_total` text,
  `raid_by` text,
  `raid_day` text,
  `community_pokemon` text,
  `community_move` text,
  `community_bonus` text,
  `community_date` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `pokestops` (
  `server_id` varchar(25) DEFAULT NULL,
  `name` tinytext,
  `lat` tinytext,
  `lon` tinytext
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `raids` (
  `server_id` varchar(25) DEFAULT NULL,
  `channel_id` varchar(25) DEFAULT NULL,
  `message_id` varchar(25) DEFAULT NULL,
  `user_id` varchar(25) DEFAULT NULL,
  `author` tinytext,
  `pokemon` varchar(20) DEFAULT NULL,
  `time` text,
  `location` text,
  `valor` text,
  `mystic` text,
  `instinct` text,
  `harmony` int(11) DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `research` (
  `server_id` varchar(25) DEFAULT NULL,
  `channel_id` varchar(25) DEFAULT NULL,
  `message_id` varchar(25) DEFAULT NULL,
  `user_id` varchar(25) DEFAULT NULL,
  `author` tinytext,
  `quest` tinytext,
  `reward` tinytext,
  `pokestop` tinytext,
  `GMT` varchar(3) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `settings` (
  `server_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `language` varchar(2) COLLATE utf8_bin DEFAULT 'US',
  `timezone` varchar(4) COLLATE utf8_bin DEFAULT '+0',
  `prefix` varchar(1) COLLATE utf8_bin DEFAULT NULL,
  `profile_channel_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `exraid_channel_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `default_raid_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `default_exraid_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `role_permission` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `log_channel_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `raid_overview_channel_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `raid_overview_message_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `event_overview_channel_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `event_overview_message_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `exraid_overview_channel_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `exraid_overview_message_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  UNIQUE KEY `server_id` (`server_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE IF NOT EXISTS `users` (
  `server_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `user_id` varchar(25) COLLATE utf8_bin DEFAULT NULL,
  `raids_created` int(11) DEFAULT '0',
  `raids_joined` int(11) NOT NULL DEFAULT '0',
  `research_created` int(11) DEFAULT '0',
  `contributor` varchar(3) COLLATE utf8_bin DEFAULT 'No',
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_index` (`server_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
