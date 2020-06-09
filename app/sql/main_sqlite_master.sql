INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'surface', 'surface', 6, 'CREATE TABLE surface (
	id INTEGER NOT NULL, 
	name VARCHAR(64), 
	PRIMARY KEY (id)
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_surface_name', 'surface', 7, 'CREATE UNIQUE INDEX ix_surface_name ON surface (name)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'alembic_version', 'alembic_version', 11, 'CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'sqlite_autoindex_alembic_version_1', 'alembic_version', 12, null);
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'item_glaze', 'item_glaze', 13, 'CREATE TABLE item_glaze (
	id INTEGER NOT NULL, 
	glaze_id INTEGER, 
	item_id INTEGER, 
	"order" INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(glaze_id) REFERENCES glaze (id), 
	FOREIGN KEY(item_id) REFERENCES item (id)
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'user', 'user', 8, 'CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(64), 
	email VARCHAR(120), 
	password_hash VARCHAR(128), 
	PRIMARY KEY (id)
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_user_email', 'user', 9, 'CREATE UNIQUE INDEX ix_user_email ON user (email)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_user_username', 'user', 14, 'CREATE UNIQUE INDEX ix_user_username ON user (username)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'clay', 'clay', 21, 'CREATE TABLE "clay"
(
	id INTEGER not null
		primary key,
	name VARCHAR(64),
	create_date DATETIME,
	delete_date DATETIME,
	user_id INTEGER
		constraint clay_user_id_fk
			references user
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_clay_create_date', 'clay', 2, 'CREATE INDEX ix_clay_create_date
	on clay (create_date)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_clay_delete_date', 'clay', 3, 'CREATE INDEX ix_clay_delete_date
	on clay (delete_date)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_clay_name', 'clay', 15, 'CREATE UNIQUE INDEX ix_clay_name
	on clay (name)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'item', 'item', 16, 'CREATE TABLE "item"
(
	id INTEGER not null
		primary key,
	name VARCHAR(64),
	description TEXT(512),
	clay_id INTEGER
		references clay,
	surface_id INTEGER
		references surface,
	temperature INTEGER,
	image_name VARCHAR(256),
	create_date DATETIME,
	delete_date DATETIME,
	user_id INTEGER
		constraint item_user_id_fk
			references user
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_item_create_date', 'item', 10, 'CREATE INDEX ix_item_create_date
	on item (create_date)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_item_delete_date', 'item', 19, 'CREATE INDEX ix_item_delete_date
	on item (delete_date)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('table', 'glaze', 'glaze', 20, 'CREATE TABLE "glaze"
(
	id INTEGER not null
		primary key,
	name VARCHAR(64),
	create_date DATETIME,
	delete_date DATETIME,
	user_id INTEGER
		constraint glaze_user_id_fk
			references user
)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_glaze_create_date', 'glaze', 4, 'CREATE INDEX ix_glaze_create_date
	on glaze (create_date)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_glaze_delete_date', 'glaze', 5, 'CREATE INDEX ix_glaze_delete_date
	on glaze (delete_date)');
INSERT INTO sqlite_master (type, name, tbl_name, rootpage, sql) VALUES ('index', 'ix_glaze_name', 'glaze', 17, 'CREATE UNIQUE INDEX ix_glaze_name
	on glaze (name)');