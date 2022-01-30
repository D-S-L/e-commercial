from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors

class database:
	def __init__(self,cursor):

		#cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		# create account table
		query = "CREATE TABLE IF NOT EXISTS `accounts` (`id` int(11) NOT NULL AUTO_INCREMENT,`username` varchar(50) NOT NULL,`password` varchar(255) NOT NULL,`email` varchar(100) NOT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"
		cursor.execute(query)
		# create customer table:
		query = "CREATE TABLE IF NOT EXISTS `customer` (`id` int PRIMARY KEY,`name` varchar(255),`address` varchar(255),`kind` ENUM ('business', 'home'));"
		cursor.execute(query)
		# create products table:
		query = "CREATE TABLE IF NOT EXISTS `products` (`id` int PRIMARY KEY,`name` varchar(255),`price` float8,`inventory` float8,`kind` varchar(255), `image` varchar(255));"
		cursor.execute(query)

		#create transactions table:
		query= "CREATE TABLE IF NOT EXISTS `transactions` (`order_id` int,`product_id` int,`product_quantity` float8,`date` datetime,`salesperson_id` int,`customer_id` int4,PRIMARY KEY (`order_id`, `product_id`));"
		cursor.execute(query)

		# create salesperson table:
		query = "CREATE TABLE IF NOT EXISTS `salesperson` (`salesperson_id` int PRIMARY KEY,`salesperson_name` varchar(255),`address` varchar(255),`email` varchar(255),`title` varchar(255),`store` varchar(255),`salary` float8);"
		cursor.execute(query)

		# create store table:
		query ="CREATE TABLE IF NOT EXISTS `store` (`store_id` varchar(255) PRIMARY KEY,`address` varchar(255),`manager` varchar(255),`num_salesperson` int,`region` int);"
		cursor.execute(query)

		#create region table
		query = "CREATE TABLE IF NOT EXISTS  `region` (`region_id` int PRIMARY KEY,`region_name` varchar(255),`region_manager` varchar(255));"
		cursor.execute(query)

		#create business table
		query = "CREATE TABLE IF NOT EXISTS  `business` (`id` int PRIMARY KEY,`business` varchar(255),`company_gross` float8,`annual_income` float8);"
		cursor.execute(query)

		#create home table
		query = "CREATE TABLE IF NOT EXISTS `home` (`id` int PRIMARY KEY,`marriage_status` ENUM ('married', 'single'),`gender` ENUM ('male', 'female'),`age` int,`income` float8);"
		cursor.execute(query)

		query = "ALTER TABLE `transactions` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);"
		cursor.execute(query)

		query = "ALTER TABLE `transactions` ADD FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`);"
		cursor.execute(query)
		query = "ALTER TABLE `transactions` ADD FOREIGN KEY (`salesperson_id`) REFERENCES `salesperson` (`salesperson_id`);"
		cursor.execute(query)

		query = "ALTER TABLE `salesperson` ADD FOREIGN KEY (`store`) REFERENCES `store` (`store_id`);"
		cursor.execute(query)
		query = "ALTER TABLE `store` ADD FOREIGN KEY (`region`) REFERENCES `region` (`region_id`);"
		cursor.execute(query)

		query="ALTER TABLE `home` ADD FOREIGN KEY (`id`) REFERENCES `customer` (`id`);"
		cursor.execute(query)

		# qurey = "ALTER TABLE `business` ADD FOREIGN KEY (`id`) REFERENCES `customer` (`id`);"
		# cursor.execute(query)
		return









