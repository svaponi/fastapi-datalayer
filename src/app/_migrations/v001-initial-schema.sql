create extension if not exists "uuid-ossp";

create table agency (
  agency_id uuid primary key not null default uuid_generate_v4(),
  agency_name varchar unique not null,
  agency_display_name varchar
);

create table auth_user (
  auth_user_id uuid primary key not null default uuid_generate_v4(),
  email varchar unique not null,
  email_verified bool not null default false,
  hashed_password varchar,
  full_name varchar
);

create table auth_user_profile (
  auth_user_profile_id uuid primary key not null default uuid_generate_v4(),
  auth_user_id uuid not null references auth_user(auth_user_id),
  auth_user_profile_type varchar not null,
  agency_id uuid references agency(agency_id),
  permissions varchar[] not null default array[]::varchar[]
);