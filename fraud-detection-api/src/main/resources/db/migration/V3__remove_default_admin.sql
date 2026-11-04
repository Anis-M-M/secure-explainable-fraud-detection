-- V3: Remove the old seeded admin account from existing databases.
-- AdminBootstrap creates a replacement from ADMIN_PASSWORD at startup.
DELETE FROM users WHERE email = 'admin@frauddetection.local';
