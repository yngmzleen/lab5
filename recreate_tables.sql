-- SQL скрипт для пересоздания таблицы пользователей в PostgreSQL

-- Удаляем старую таблицу, если существует
DROP TABLE IF EXISTS users CASCADE;

-- Создание таблицы users с правильной структурой
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Создание индекса для быстрого поиска по email
CREATE INDEX idx_users_email ON users(email);

