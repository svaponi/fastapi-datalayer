create extension if not exists "uuid-ossp";

create table chat (
  chat_id uuid primary key not null default uuid_generate_v4(),
  auth_user_ids uuid[] not null default array[]::uuid[]
);

create table chat_message (
  chat_message_id uuid primary key not null default uuid_generate_v4(),
  chat_id uuid not null references chat(chat_id),
  auth_user_id uuid not null references auth_user(auth_user_id),
  entered_at timestamp not null default now(),
  content varchar
);

create table chat_message_media (
  chat_message_media_id uuid primary key not null default uuid_generate_v4(),
  chat_message_id uuid not null references chat_message(chat_message_id),
  auth_user_id uuid not null references auth_user(auth_user_id),
  subscription_info varchar
);