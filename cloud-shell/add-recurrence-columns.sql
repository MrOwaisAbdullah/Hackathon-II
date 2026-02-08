-- Migration script to add recurring task columns to tasks table
-- Run this directly on your Neon database

ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_settings JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_instance_id UUID REFERENCES tasks(id);
