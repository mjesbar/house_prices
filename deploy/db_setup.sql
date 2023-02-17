
GRANT SESSION_VARIABLES_ADMIN ON *.* TO 'houseprices'@'%';

USE houseprices;

DROP TABLE IF EXISTS dataset;

CREATE TABLE IF NOT EXISTS dataset(
    id              INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    link_index      INT NOT NULL,
    code            VARCHAR(100),
    neighborhood    VARCHAR(100),
    city            VARCHAR(100),
    offer_type      VARCHAR(100),
    property_type   VARCHAR(100),
    rooms           SMALLINT,
    baths           SMALLINT,
    parking_lots    TINYINT,
    built_area      INT,
    private_area    INT,
    stratus         TINYINT,
    price           INT,
    priceArea       INT,
    old             VARCHAR(10)
);

-- echo "link_index,Code,Neighborhood,City,Offer_type,Property_type,Rooms,Baths,Parking_lots,Built_area,Private_area,Stratus,Price,Price/Area,Old\n" \
LOAD DATA LOCAL INFILE '/home/debian/mega/xlocal/house_prices/data/datamerge.csv'
    INTO TABLE dataset
    CHARACTER SET UTF8
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;
