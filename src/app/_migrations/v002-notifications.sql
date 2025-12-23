create extension if not exists "uuid-ossp";

create table user_device (
  user_device_id uuid primary key not null default uuid_generate_v4(),
  auth_user_id uuid not null references auth_user(auth_user_id),
  subscription_info varchar
);