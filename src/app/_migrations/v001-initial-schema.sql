create extension if not exists "uuid-ossp";

create table if not exists users
(
    id         uuid primary key default uuid_generate_v4(),
    email      varchar unique not null,
    name       varchar,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);
