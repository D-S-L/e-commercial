
CREATE TABLE `customer` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `address` varchar(255),
  `kind` ENUM ('business', 'home')
);

CREATE TABLE `products` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `price` float8,
  `inventory` float8,
  `kind` varchar(255)
);

CREATE TABLE `transactions` (
  `order_id` int,
  `product_id` int,
  `product_quantity` float8,
  `date` datetime,
  `salesperson_id` int,
  `customer_id` int4,
  PRIMARY KEY (`order_id`, `product_id`)
);

CREATE TABLE `salesperson` (
  `salesperson_id` int PRIMARY KEY,
  `salesperson_name` varchar(255),
  `address` varchar(255),
  `email` varchar(255),
  `title` varchar(255),
  `store` varchar(255),
  `salary` float8
);

CREATE TABLE `store` (
  `store_id` varchar(255) PRIMARY KEY,
  `address` varchar(255),
  `manager` varchar(255),
  `num_salesperson` int,
  `region` int
);

CREATE TABLE `region` (
  `region_id` int PRIMARY KEY,
  `region_name` varchar(255),
  `region_manager` varchar(255)
);

CREATE TABLE `business` (
  `id` int PRIMARY KEY,
  `business` varchar(255),
  `company_gross` float8,
  `annual_income` float8
);

CREATE TABLE `home` (
  `id` int PRIMARY KEY,
  `marriage_status` ENUM ('married', 'single'),
  `gender` ENUM ('male', 'female'),
  `age` int,
  `income` float8
);

ALTER TABLE `transactions` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`salesperson_id`) REFERENCES `salesperson` (`salesperson_id`);

ALTER TABLE `salesperson` ADD FOREIGN KEY (`store`) REFERENCES `store` (`store_id`);

ALTER TABLE `store` ADD FOREIGN KEY (`region`) REFERENCES `region` (`region_id`);

ALTER TABLE `home` ADD FOREIGN KEY (`id`) REFERENCES `customer` (`id`);

ALTER TABLE `business` ADD FOREIGN KEY (`id`) REFERENCES `customer` (`id`);

