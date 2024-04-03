---- FORMATS ----
-- TIME:     "HH:MM"
-- DATE:     "YYYY-MM-DD"
-- DATETIME: "YYYY-MM-DD HH:MM"


---- CREATE TABLES ----

CREATE TABLE employee (
 id INTEGER PRIMARY KEY,
 forename VARCHAR(20) NOT NULL,
 surname VARCHAR(30) NOT NULL,
 security_hash CHAR(77) NOT NULL,
 role CHAR(1) NOT NULL CHECK(role IN('S','C','M','A')) -- role is denoted by its first character. S(taff), C(hef), M(anager), A(dmin)
);

CREATE TABLE menu_category (
 id INTEGER PRIMARY KEY,
 name VARCHAR(50)
);

CREATE TABLE menu_item (
 id INTEGER PRIMARY KEY,
 category_id INTEGER,
 price FLOAT,
 name VARCHAR(50),
 description VARCHAR(100),
 allergens VARCHAR(10),
 FOREIGN KEY (category_id) REFERENCES menu_category(id)
);

CREATE TABLE inventory_item (
 name VARCHAR(50) PRIMARY KEY,
 amount INTEGER,
 restock_at INTEGER
);

CREATE TABLE `order` (
 id INTEGER PRIMARY KEY,
 name VARCHAR(40),
 placed_at DATETIME,
 amount_paid FLOAT, -- Store the amount paid for future reports
 status VARCHAR(10)
);

CREATE TABLE order_item(
 item_id INTEGER,
 order_id INTEGER,
 quantity INTEGER,
 FOREIGN KEY(order_id) REFERENCES `order`(id)
);

CREATE TABLE reservation (
 id INTEGER PRIMARY KEY,
 `table` INTEGER,
 amount INTEGER,
 name VARCHAR(50),
 datetime DATETIME,
 FOREIGN KEY('table') REFERENCES 'table'(id)
);

CREATE TABLE `table` (
 id INTEGER PRIMARY KEY,
 capacity INTEGER
);

CREATE TABLE event (
 id INTEGER PRIMARY KEY,
 name VARCHAR(40),
 datetime DATETIME
 description VARCHAR(200)
);

CREATE TABLE discount (
 code VARCHAR(40) PRIMARY KEY,
 amount FLOAT,
 is_percentage INTEGER CHECK(is_percentage IN(0,1)),
  --| 0: A flat amount is reduced ( price = price-amount )
  --| 1: A percent discount is applied ( price = price * (1-amount) )
  --|     If it's a percentage, make sure the amount is limited between 0 and 1.

 invert_applicables INTEGER CHECK(invert_applicables IN(0,1))
  --| 0: Only the attached discount_items get the discount
  --| 1: The discount can be used on anything besides the attached items.
);

CREATE TABLE discount_item (
 code VARCHAR(40),
 item_id INTEGER
);

insert into employee(forename, surname, role, security_hash) values
("admin", "istrator", "A", "$5$rounds=535000$bKnJQj.x4iFQ6Yy6$z.V9RPys8Lx4BVfj2pi.iB1jfxoUeg8wAmCsOFIbhZ9"), -- Password is 'admin'
("steve", "zuckerberg", "C", "$5$rounds=535000$EbutSNeTrx/9dwOh$kIRAw31lakZ3PvENvCNagTrSBSnmyF8mrQ9MMhG5qfB"); -- Password is 'password'

insert into menu_category(id, name) values(1, "Grub");

insert into menu_item(category_id, price, name, description, allergens)
(1, 3, "Scary Cola", "Do not pscare yourself", "None"),
(1, 8, "Flapples", "Exotic fruit from Manicarca", "G");

insert into inventory_item(name, amount, restock_at)
("Scary Cola", 25, 10),
("Flappes", 20, 10),
("Fork", 100, 50);

insert into `table`(capacity) values
(4), (4), (4), (2), (2), (2), (2), (2), (2), (6);
