create extension if not exists "uuid-ossp";

create table agency (
  agency_id uuid primary key not null default uuid_generate_v4(),
  agency_name varchar unique not null,
  agency_display_name varchar
);

-- we cannot use "user" as a table name since it is a reserved keyword in postgres
create table user_account (
  user_id uuid primary key not null default uuid_generate_v4(),
  email varchar unique not null,
  email_verified bool not null default false,
  hashed_password varchar,
  full_name varchar
);

create table user_auth (
  user_auth_id uuid primary key not null default uuid_generate_v4(),
  user_id uuid not null references user_account(user_id),
  user_type varchar not null,
  agency_id uuid references agency(agency_id),
  permissions varchar[]
);

create table user_device (
  user_device_id uuid primary key not null default uuid_generate_v4(),
  user_id uuid not null references user_account(user_id),
  subscription_info varchar
);

create table chat (
  chat_id uuid primary key not null default uuid_generate_v4(),
  chat_title varchar,
  user_ids uuid[]
);

create table chat_message (
  chat_message_id uuid primary key not null default uuid_generate_v4(),
  chat_id uuid not null references chat(chat_id),
  from_user_id uuid not null references user_account(user_id),
  entered_at timestamp not null default now(),
  content varchar
);

create table chat_message_to_user (
  chat_message_to_user_id uuid primary key not null default uuid_generate_v4(),
  chat_message_id uuid not null references chat_message(chat_message_id),
  to_user_id uuid not null references user_account(user_id),
  read_at timestamp
);