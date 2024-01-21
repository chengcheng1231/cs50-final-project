# YOUR PROJECT TITLE

#### Video Demo: https://www.youtube.com/watch?v=r3HjzN1bPPs&ab_channel=ChengchengHsu

#### Prject Name: What to eat?

#### Description:

This project is a web application that allows users to add shop, meal and select meal for each day.
User Story:

1. I can register and login to the website.
2. I can add shop and meal to the website.
3. I can select meal for each day.
4. I can see the result of the meal selection.
5. I can see the statistics of the meal selection for selected date.

#### Database Schema:

```
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);

CREATE TABLE shops (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL);

CREATE TABLE meals (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, price INTEGER NO NULL, shop_id INTEGER, FOREIGN KEY(shop_id) REFERENCES shops(id));

CREATE TABLE meal_records (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, time DATETIME NOT NULL, shop_id INTEGER, FOREIGN KEY(shop_id) REFERENCES shops(id));

CREATE TABLE user_meal_records (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER, meal_record_id INTEGER, meal_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(meal_record_id) REFERENCES meal_records(id), FOREIGN KEY(meal_id) REFERENCES meals(id));
```
