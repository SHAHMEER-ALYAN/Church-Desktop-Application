-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 28, 2025 at 02:24 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `churchapp`
--

-- --------------------------------------------------------

--
-- Table structure for table `bag_offering`
--

CREATE TABLE `bag_offering` (
  `bag_id` int(11) NOT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `member_id` int(11) DEFAULT NULL,
  `service_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `donation`
--

CREATE TABLE `donation` (
  `donation_id` int(11) NOT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `member_id` int(11) DEFAULT NULL,
  `donation_type` enum('general','building','charity','event','special','youth','mission','other') DEFAULT 'general',
  `donation_date` date NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `comment` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `donation`
--

INSERT INTO `donation` (`donation_id`, `transaction_id`, `member_id`, `donation_type`, `donation_date`, `amount`, `comment`) VALUES
(1, 'd5a53c5a-7346-43b0-845b-896a56aca0b2', 1, 'general', '2025-10-28', 5000.00, 'This is test donation');

-- --------------------------------------------------------

--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `expense_id` int(11) NOT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `expense_type` enum('Repair & Maintenance','Utilities','Water (Tanker & Drinking Water)','Event','Fuel','Staff Salary','Clergy Allowances','Refreshment','Office Expenses','Financial Support','Staff Loan','Pastor Loan','Diocese Loan') DEFAULT NULL,
  `receipt_number` varchar(50) DEFAULT NULL,
  `comments` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (`expense_id`, `transaction_id`, `expense_type`, `receipt_number`, `comments`) VALUES
(2, 'acd73ccd-562b-41e8-89c0-9f402bb3b67e', 'Event', 'RN100', 'Test Event');

-- --------------------------------------------------------

--
-- Table structure for table `members`
--

CREATE TABLE `members` (
  `member_id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `nic_no` varchar(20) DEFAULT NULL,
  `membership_card_no` varchar(20) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `join_date` date DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT 'active',
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `members`
--

INSERT INTO `members` (`member_id`, `first_name`, `last_name`, `email`, `phone`, `nic_no`, `membership_card_no`, `date_of_birth`, `join_date`, `status`, `created_at`, `updated_at`) VALUES
(1, 'Test', 'Person', 'test@gmail.com', '0333123123', '45504123123', 'CC123', '2025-10-26', '2025-10-26', 'active', '2025-10-26 03:17:31', '2025-10-26 03:17:31'),
(2, 'abc', 'abc', 'abc@gmail.com', '03333333333', '123123123123123', '12312', '2025-10-26', '2025-10-26', 'active', '2025-10-26 10:33:15', '2025-10-26 10:33:15'),
(3, 'New', 'Person', 'person@gmail.com', '0333333333', '1234567891234', '1234', '2025-10-26', '2025-10-26', 'active', '2025-10-26 11:04:02', '2025-10-26 11:04:02');

-- --------------------------------------------------------

--
-- Table structure for table `membership`
--

CREATE TABLE `membership` (
  `membership_id` int(11) NOT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `member_id` int(11) DEFAULT NULL,
  `payment_month` date DEFAULT NULL,
  `payment_year` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `membership`
--

INSERT INTO `membership` (`membership_id`, `transaction_id`, `member_id`, `payment_month`, `payment_year`) VALUES
(1, '961ef976-2600-4809-a556-f6b912a81b29', 1, '2025-01-01', 2025),
(2, '1aa99e3f-0295-4ae5-ae1d-06e4c3f89c88', 1, '2025-02-01', 2025),
(3, '40413ab8-0291-4e37-bc8d-d478714e8e74', 1, '2025-03-01', 2025),
(4, '3c560e6e-2afb-40ec-9693-30d822e87849', 1, '2025-04-01', 2025),
(5, '6faf58ee-abf3-4cb9-b109-3e2430a3fc1c', 1, '2025-05-01', 2025),
(6, 'ea54026a-ba05-4649-821d-ee3b1918db49', 1, '2025-06-01', 2025),
(7, '9760b443-3326-42d6-8bae-3dae3dcf2e25', 1, '2025-07-01', 2025),
(8, 'cb0d9532-4f40-4df8-92d7-372777031d36', 1, '2025-08-01', 2025);

-- --------------------------------------------------------

--
-- Table structure for table `parking`
--

CREATE TABLE `parking` (
  `parking_id` int(11) NOT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `member_id` int(11) DEFAULT NULL,
  `vehicle_number` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `thanksgiving`
--

CREATE TABLE `thanksgiving` (
  `thanksgiving_id` int(11) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `purpose` varchar(255) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `thanksgiving`
--

INSERT INTO `thanksgiving` (`thanksgiving_id`, `member_id`, `transaction_id`, `purpose`, `comment`, `date`) VALUES
(1, 1, 'eb91c09d-6806-4d29-b213-e59aee59c143', 'General Thanksgiving', 'test thanksgiving', '2025-10-28');

-- --------------------------------------------------------

--
-- Table structure for table `tithe`
--

CREATE TABLE `tithe` (
  `tithe_id` int(11) NOT NULL,
  `transaction_id` varchar(36) DEFAULT NULL,
  `member_id` int(11) DEFAULT NULL,
  `tithe_month` date DEFAULT NULL,
  `tithe_year` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tithe`
--

INSERT INTO `tithe` (`tithe_id`, `transaction_id`, `member_id`, `tithe_month`, `tithe_year`) VALUES
(2, '8e72bfea-5c6d-41a4-8db2-ee6665eabacd', 3, '2025-01-01', 2025),
(3, 'b3535f1b-54d3-44f3-b3ec-02d044485108', 3, '2025-02-01', 2025),
(4, '776cc671-110f-4804-96e2-dfccdf6c93b7', 1, '2025-01-01', 2025);

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `transaction_id` varchar(36) NOT NULL,
  `member_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `transaction_type` enum('membership','tithe','donation','bag_offering','parking','thanksgiving','expense') DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `transaction_date` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`transaction_id`, `member_id`, `user_id`, `transaction_type`, `amount`, `transaction_date`, `created_at`, `updated_at`) VALUES
('1aa99e3f-0295-4ae5-ae1d-06e4c3f89c88', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 03:49:50', '2025-10-26 03:49:50'),
('3c560e6e-2afb-40ec-9693-30d822e87849', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 04:09:09', '2025-10-26 04:09:09'),
('40413ab8-0291-4e37-bc8d-d478714e8e74', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 03:49:50', '2025-10-26 03:49:50'),
('6faf58ee-abf3-4cb9-b109-3e2430a3fc1c', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 04:10:52', '2025-10-26 04:10:52'),
('776cc671-110f-4804-96e2-dfccdf6c93b7', 1, 1, 'tithe', 8000.00, '2025-10-28', '2025-10-28 16:04:57', '2025-10-28 16:04:57'),
('8e72bfea-5c6d-41a4-8db2-ee6665eabacd', 3, 1, 'tithe', 500.00, '2025-10-26', '2025-10-26 11:27:52', '2025-10-26 11:27:52'),
('961ef976-2600-4809-a556-f6b912a81b29', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 03:49:50', '2025-10-26 03:49:50'),
('9760b443-3326-42d6-8bae-3dae3dcf2e25', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 04:17:59', '2025-10-26 04:17:59'),
('acd73ccd-562b-41e8-89c0-9f402bb3b67e', NULL, 1, 'expense', -1000.00, '2025-10-26', '2025-10-26 06:12:40', '2025-10-26 06:12:40'),
('b3535f1b-54d3-44f3-b3ec-02d044485108', 3, 1, 'tithe', 500.00, '2025-10-26', '2025-10-26 11:43:14', '2025-10-26 11:43:14'),
('cb0d9532-4f40-4df8-92d7-372777031d36', 1, 1, 'membership', 1000.00, '2025-10-28', '2025-10-28 16:00:29', '2025-10-28 16:00:29'),
('d5a53c5a-7346-43b0-845b-896a56aca0b2', 1, 1, 'donation', 5000.00, '2025-10-28', '2025-10-28 16:57:12', '2025-10-28 16:57:12'),
('ea54026a-ba05-4649-821d-ee3b1918db49', 1, 1, 'membership', 1000.00, '2025-10-26', '2025-10-26 04:13:56', '2025-10-26 04:13:56'),
('eb91c09d-6806-4d29-b213-e59aee59c143', 1, 1, 'thanksgiving', 500.00, '2025-10-28', '2025-10-28 17:53:15', '2025-10-28 17:53:15');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `role` enum('admin','staff') DEFAULT 'staff',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password_hash`, `full_name`, `role`, `created_at`) VALUES
(1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Administrator', 'admin', '2025-10-26 03:15:45');

-- --------------------------------------------------------

--
-- Stand-in structure for view `v_all_transactions`
-- (See below for the actual view)
--
CREATE TABLE `v_all_transactions` (
`transaction_id` varchar(36)
,`transaction_type` enum('membership','tithe','donation','bag_offering','parking','thanksgiving','expense')
,`amount` decimal(10,2)
,`transaction_date` date
,`member_id` int(11)
,`member_name` varchar(201)
,`entered_by` varchar(100)
,`created_at` datetime
);

-- --------------------------------------------------------

--
-- Structure for view `v_all_transactions`
--
DROP TABLE IF EXISTS `v_all_transactions`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_all_transactions`  AS SELECT `t`.`transaction_id` AS `transaction_id`, `t`.`transaction_type` AS `transaction_type`, `t`.`amount` AS `amount`, `t`.`transaction_date` AS `transaction_date`, `m`.`member_id` AS `member_id`, concat(`m`.`first_name`,' ',`m`.`last_name`) AS `member_name`, `u`.`full_name` AS `entered_by`, `t`.`created_at` AS `created_at` FROM ((`transactions` `t` left join `members` `m` on(`t`.`member_id` = `m`.`member_id`)) left join `users` `u` on(`t`.`user_id` = `u`.`user_id`)) ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bag_offering`
--
ALTER TABLE `bag_offering`
  ADD PRIMARY KEY (`bag_id`),
  ADD KEY `transaction_id` (`transaction_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `donation`
--
ALTER TABLE `donation`
  ADD PRIMARY KEY (`donation_id`),
  ADD KEY `transaction_id` (`transaction_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`expense_id`),
  ADD KEY `transaction_id` (`transaction_id`);

--
-- Indexes for table `members`
--
ALTER TABLE `members`
  ADD PRIMARY KEY (`member_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `phone` (`phone`),
  ADD UNIQUE KEY `nic_no` (`nic_no`),
  ADD UNIQUE KEY `membership_card_no` (`membership_card_no`);

--
-- Indexes for table `membership`
--
ALTER TABLE `membership`
  ADD PRIMARY KEY (`membership_id`),
  ADD KEY `transaction_id` (`transaction_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `parking`
--
ALTER TABLE `parking`
  ADD PRIMARY KEY (`parking_id`),
  ADD KEY `transaction_id` (`transaction_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `thanksgiving`
--
ALTER TABLE `thanksgiving`
  ADD PRIMARY KEY (`thanksgiving_id`),
  ADD KEY `member_id` (`member_id`),
  ADD KEY `transaction_id` (`transaction_id`);

--
-- Indexes for table `tithe`
--
ALTER TABLE `tithe`
  ADD PRIMARY KEY (`tithe_id`),
  ADD KEY `transaction_id` (`transaction_id`),
  ADD KEY `member_id` (`member_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`transaction_id`),
  ADD KEY `member_id` (`member_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bag_offering`
--
ALTER TABLE `bag_offering`
  MODIFY `bag_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `donation`
--
ALTER TABLE `donation`
  MODIFY `donation_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
  MODIFY `expense_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `members`
--
ALTER TABLE `members`
  MODIFY `member_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `membership`
--
ALTER TABLE `membership`
  MODIFY `membership_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `parking`
--
ALTER TABLE `parking`
  MODIFY `parking_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `thanksgiving`
--
ALTER TABLE `thanksgiving`
  MODIFY `thanksgiving_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tithe`
--
ALTER TABLE `tithe`
  MODIFY `tithe_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bag_offering`
--
ALTER TABLE `bag_offering`
  ADD CONSTRAINT `bag_offering_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `bag_offering_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `donation`
--
ALTER TABLE `donation`
  ADD CONSTRAINT `donation_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `donation_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
  ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `membership`
--
ALTER TABLE `membership`
  ADD CONSTRAINT `membership_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `membership_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `parking`
--
ALTER TABLE `parking`
  ADD CONSTRAINT `parking_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `parking_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `thanksgiving`
--
ALTER TABLE `thanksgiving`
  ADD CONSTRAINT `thanksgiving_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `thanksgiving_ibfk_2` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE;

--
-- Constraints for table `tithe`
--
ALTER TABLE `tithe`
  ADD CONSTRAINT `tithe_ibfk_1` FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tithe_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
